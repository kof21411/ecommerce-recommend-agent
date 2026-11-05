"""基于数据库商品的 LangGraph 推荐流程。"""
import asyncio
import json
import logging
from decimal import Decimal
from typing import Any, TypedDict
from uuid import UUID

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import Category, Product
from rag.product_index import search_product_ids
from agents.intent import classify_intent, parse_budget, search_terms

logger = logging.getLogger(__name__)


class State(TypedDict, total=False):
    """推荐工作流的共享状态；total=False 表示各字段可由不同节点逐步填充。"""
    query: str  # 用户的原始购物需求
    budget: float | None  # 用户显式指定的预算上限；未指定时可从 query 解析
    category: str | None  # 用户显式指定的商品分类名称
    candidates: list[dict]  # 检索并经数据库过滤后的候选商品
    items: list[dict]  # 最终推荐项，包含商品、分数和推荐理由
    degraded: bool  # 检索或排序是否使用了降级方案
    review_passed: bool  # 排序结果是否通过当前校验
    retries: int  # 排序结果未通过校验的次数，用于限制重试
    content: str  # 返回给用户的说明文本
    message: str | None  # 空结果或降级等附加提示


def serialize(product):
    return {"id": str(product.id), "name": product.name, "description": product.description,
            "price": float(product.price), "brand": product.brand, "stock": product.stock,
            "rating": product.rating, "image_url": product.image_url,
            "attributes": product.attributes or {}, "sales_count": product.sales_count,
            "review_count": product.review_count}


class RecommendationOrchestrator:
    def __init__(self, db : AsyncSession):
        self.db = db

        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL, 
            api_key=settings.OPENAI_API_KEY, 
            temperature=0, 
            request_timeout=30
        )

        graph = StateGraph(State)
        graph.add_node("retrieve", self.retrieve)
        graph.add_node("rank", self.rank)
        graph.add_node("review", self.review)
        graph.add_node("fallback", self.fallback)
        graph.add_node("empty", self.empty)
        graph.set_entry_point("retrieve")
        graph.add_conditional_edges("retrieve", lambda s: "rank" if s["candidates"] else "empty")
        graph.add_edge("rank", "review")
        graph.add_conditional_edges("review", lambda s: END if s.get("review_passed") else ("rank" if s.get("retries", 0) < 2 else "fallback"), {END: END, "rank": "rank", "fallback": "fallback"})
        graph.add_edge("fallback", END)
        graph.add_edge("empty", END)
        self.graph = graph.compile()

    async def retrieve(self, state : State) -> State:
        query = state["query"]
        budget = state.get("budget")
        if budget is None:
            budget = parse_budget(query)
        conditions = [Product.status == "active", Product.stock > 0]
        if budget is not None:
            conditions.append(Product.price <= Decimal(str(budget)))
        if state.get("category"):
            conditions.append(Product.category_id.in_(select(Category.id).where(Category.name.ilike(state["category"]))))
        degraded = False
        try:
            ids = []
            for value in await search_product_ids(query, top_k=50):
                try:
                    ids.append(UUID(value))
                except (TypeError, ValueError):
                    continue
        except Exception:
            logger.exception("Vector retrieval failed; using database search")
            degraded = True
            tokens = search_terms(query)
            if not tokens:
                products = []
            else:
                predicates = [or_(Product.name.ilike(f"%{word}%"), Product.description.ilike(f"%{word}%"), Product.brand.ilike(f"%{word}%")) for word in tokens]
                products = (await self.db.execute(select(Product).where(*conditions, or_(*predicates)).order_by(Product.sales_count.desc()).limit(20))).scalars().all()
        else:
            products = (await self.db.execute(select(Product).where(*conditions, Product.id.in_(ids)))).scalars().all() if ids else []
            by_id = {p.id: p for p in products}
            products = [by_id[i] for i in dict.fromkeys(ids) if i in by_id]
        return {"candidates": [serialize(p) for p in products[:20]], "degraded": degraded, "retries": 0}

    async def rank(self, state : State) -> State:
        try:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            # llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0, request_timeout=30)
            response = await asyncio.wait_for(self.llm.ainvoke([
                ("system", "只根据候选商品排序，返回 JSON 对象 {\"ids\": [\"商品ID\"]}，不要编造商品。"),
                ("human", json.dumps({"query": state["query"], "products": state["candidates"]}, ensure_ascii=False)),
            ]), timeout=35)
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            ids = json.loads(text)["ids"]
            by_id = {p["id"]: p for p in state["candidates"]}
            if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or any(i not in by_id for i in ids):
                raise ValueError("Invalid ranked IDs")
            # 固定理由来自可信商品字段，不依赖模型生成的事实。
            return {"items": [{"product": by_id[i], "score": None, "reason": "根据商品信息及您的筛选条件推荐"} for i in ids[:5]], "review_passed": True}
        except Exception:
            logger.warning("Ranking unavailable or invalid", exc_info=True)
            return {"items": [], "review_passed": False}

    async def review(self, state: State):
        if state.get("review_passed"):
            return {"content": "根据您的需求找到以下商品。", "message": None}
        return {"retries": state.get("retries", 0) + 1}

    async def fallback(self, state : State):
        return {"items": [{"product": p, "score": None, "reason": "按商品检索结果推荐"} for p in state["candidates"][:5]], "degraded": True, "content": "模型排序不可用，展示检索结果。", "message": "排序已降级"}

    async def empty(self, state : State):
        return {"items": [], "content": "没有找到符合条件的商品。", "message": "暂无匹配商品"}

    async def recommend(self, query, budget=None, category=None):
        return await self.graph.ainvoke({"query": query, "budget": budget, "category": category})

    async def stream_message(self, message, history):
        """输出前端事件；推荐排序的内部 JSON 在校验前不对外输出。"""
        intent = classify_intent(message)
        if intent == "chat":
            if not settings.OPENAI_API_KEY:
                yield {"type": "chunk", "content": "你好！请告诉我你想寻找的商品。"}
                return
            messages = [("system", "你是购物助手。不要编造商品、价格或规格。")]
            messages.extend((m["role"], m["content"]) for m in history[-10:] if m["role"] in ("user", "assistant"))
            messages.append(("user", message))
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield {"type": "chunk", "content": chunk.content}
            return

        yield {"type": "chunk", "content": "正在检索商品…\n\n"}
        state = {}
        async for update in self.graph.astream({"query": message, "budget": None, "category": None}, stream_mode="updates"):
            for node, values in update.items():
                if not isinstance(values, dict):
                    continue
                state.update(values)
                if node == "retrieve" and values.get("candidates"):
                    yield {"type": "chunk", "content": "已找到候选商品，正在整理结果…\n\n"}
        content = state.get("content", "")
        if intent in ("qa", "compare") and state.get("items"):
            content = "以下是数据库中找到的相关商品信息；未提供的规格无法确认。"
        if content:
            yield {"type": "chunk", "content": content}
        yield {"type": "products", "items": state.get("items", [])}

    async def process_message(self, message, history):
        intent = classify_intent(message)
        if intent == "chat":
            if not settings.OPENAI_API_KEY:
                return {"content": "你好！请告诉我你想寻找的商品。", "items": [], "intent": intent}
            # llm = ChatOpenAI(model=settings.OPENAI_MODEL_FAST, api_key=settings.OPENAI_API_KEY, temperature=0.7, request_timeout=30)
            messages = [("system", "你是购物助手。不要编造商品、价格或规格。")]
            messages.extend((m["role"], m["content"]) for m in history[-10:] if m["role"] in ("user", "assistant"))
            messages.append(("user", message))
            response = await asyncio.wait_for(self.llm.ainvoke(messages), timeout=35)
            return {"content": response.content, "items": [], "intent": intent}
        result = await self.recommend(message)
        result["intent"] = intent
        if intent in ("qa", "compare") and result["items"]:
            result["content"] = "以下是数据库中找到的相关商品信息；未提供的规格无法确认。"
        return result

"""评审Agent — 推荐质量审核"""
import json
import logging
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import settings

logger = logging.getLogger("ecom_agent.critic")


class CriticAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
            max_tokens=500,
        )
        self.prompt = """You are a recommendation quality reviewer. Score 1-10.
Dimensions: relevance, diversity, value, explanation quality.
Output JSON: {"score": N, "feedback": "..."}"""

    async def review(self, results: str, query: str) -> Dict[str, Any]:
        msg = f"Review recommendation:\n{results}\n\nOriginal query: {query}"
        try:
            resp = await self.llm.ainvoke([SystemMessage(content=self.prompt), HumanMessage(content=msg)])
            cleaned = resp.content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {"score": 7, "feedback": "Review unavailable"}

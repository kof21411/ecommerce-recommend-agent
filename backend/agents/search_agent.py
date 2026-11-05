"""搜索Agent — 语义搜索 + 智能排序"""
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import settings


class SearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
            max_tokens=settings.AGENT_MAX_TOKENS,
            streaming=True,
        )
        self.system_prompt = """You are an e-commerce search expert.

Given a user query and candidate products, rank and filter the most relevant products.

Output format for each product:
- Product name
- Price
- Why it matches (1-2 sentences)
- Match score (1-10)

Sort by relevance to the user's needs."""

    async def search(self, query: str, knowledge: str = "") -> AsyncGenerator[str, None]:
        text = f"User query: {query}"
        if knowledge:
            text += f"\n\n{knowledge}"
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=text)]
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

"""推荐Agent — 个性化推荐 + 推荐理由"""
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import settings


class RecommendAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            max_tokens=settings.AGENT_MAX_TOKENS,
            streaming=True,
        )
        self.system_prompt = """You are a personalized recommendation expert.

Given user preferences, browsing history, and candidate products:
1. Analyze what the user truly needs
2. Recommend the top 5 most suitable products
3. For each product provide:
   - Name, price, key features
   - Why this user would like it (personalized reason)
   - Match score (1-10)
4. Be persuasive but honest"""

    async def recommend(self, query: str, user_id: str, knowledge: str = "") -> AsyncGenerator[str, None]:
        text = f"User request: {query}\nUser ID: {user_id}"
        if knowledge:
            text += f"\n\n{knowledge}"
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=text)]
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

"""问答Agent — 商品咨询 + 对比分析"""
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import settings


class QAAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.5,
            max_tokens=settings.AGENT_MAX_TOKENS,
            streaming=True,
        )
        self.qa_prompt = """You are a product knowledge expert. Answer questions accurately based on the provided product information."""
        self.compare_prompt = """You are a product comparison expert. Compare products on:
1. Key specs
2. Pros and cons
3. Best for which use case
4. Value for money
Provide a clear, structured comparison."""

    async def answer(self, question: str, knowledge: str = "") -> AsyncGenerator[str, None]:
        text = f"Question: {question}"
        if knowledge:
            text += f"\n\n{knowledge}"
        messages = [SystemMessage(content=self.qa_prompt), HumanMessage(content=text)]
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

    async def compare(self, question: str, knowledge: str = "") -> AsyncGenerator[str, None]:
        text = f"Compare: {question}"
        if knowledge:
            text += f"\n\n{knowledge}"
        messages = [SystemMessage(content=self.compare_prompt), HumanMessage(content=text)]
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

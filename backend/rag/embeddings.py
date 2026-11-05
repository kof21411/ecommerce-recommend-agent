"""嵌入服务 — text-embedding-3-small 1536维"""
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings

from config import settings


class EmbeddingService:
    def __init__(self):
        self._embeddings: Optional[OpenAIEmbeddings] = None

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        # 延迟初始化，避免未配置 OPENAI_API_KEY 时应用启动即失败
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL, api_key=settings.OPENAI_API_KEY)
        return self._embeddings

    async def embed_text(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)


embedding_service = EmbeddingService()

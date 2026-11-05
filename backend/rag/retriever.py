"""RAG检索器 — 商品知识检索"""
import logging
from typing import Dict, List

from config import settings
from rag.embeddings import embedding_service
from rag.vector_store import VectorStoreManager

logger = logging.getLogger("ecom_agent.retriever")


class ProductRetriever:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.embeddings = embedding_service

    async def search(self, query: str, top_k: int = None) -> List[Dict]:
        top_k = top_k or settings.RAG_TOP_K
        try:
            qv = await self.embeddings.embed_text(query)
            raw = self.vector_store.search(settings.CHROMA_COLLECTION, qv, top_k)
            return [
                {
                    "title": r["metadata"].get("title", "?"),
                    "content": r["content"],
                    "category": r["metadata"].get("category", "?"),
                    "score": round(1 - (r["distance"] or 0), 4),
                }
                for r in raw
                if (1 - (r["distance"] or 0)) >= settings.RAG_SCORE_THRESHOLD
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

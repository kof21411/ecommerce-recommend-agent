"""ChromaDB向量存储"""
import logging

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings

logger = logging.getLogger("ecom_agent.vector_store")
_chroma_client = None


def _chroma_settings() -> ChromaSettings:
    # HttpClient 会原地修改 settings，因此每次创建独立实例
    return ChromaSettings(anonymized_telemetry=False)


async def init_vector_store():
    global _chroma_client
    try:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=_chroma_settings(),
        )
        _chroma_client.heartbeat()
        logger.info("Connected to ChromaDB at %s:%s", settings.CHROMA_HOST, settings.CHROMA_PORT)
    except Exception as exc:
        logger.warning("ChromaDB unavailable: %s", exc)
        _chroma_client = None


def get_vector_store():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT, settings=_chroma_settings())
    return _chroma_client


class VectorStoreManager:
    def __init__(self):
        self.client = get_vector_store()

    def get_or_create_collection(self, name=None):
        # 使用余弦距离，retriever 中按 1 - distance 计算相似度
        return self.client.get_or_create_collection(
            name=name or settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, collection_name, query_embedding, top_k=5, where=None):
        col = self.get_or_create_collection(collection_name)
        kwargs = {"query_embeddings": [query_embedding], "n_results": top_k}
        if where:
            kwargs["where"] = where
        results = col.query(**kwargs)
        formatted = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    }
                )
        return formatted

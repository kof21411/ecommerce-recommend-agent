"""商品向量索引：PostgreSQL 为事实源。"""
import asyncio
import json

from config import settings
from rag.embeddings import embedding_service
from rag.vector_store import VectorStoreManager


def product_text(product):
    return "\n".join(filter(None, [product.name, product.brand or "", product.description or "", json.dumps(product.attributes or {}, ensure_ascii=False, sort_keys=True)]))


async def index_product(product):
    text = product_text(product)
    vector = await asyncio.wait_for(embedding_service.embed_text(text), timeout=settings.INDEX_TIMEOUT_SECONDS)

    def write():
        collection = VectorStoreManager().get_or_create_collection()
        collection.upsert(ids=[f"product:{product.id}"], documents=[text], embeddings=[vector],
                          metadatas=[{"product_id": str(product.id), "type": "product"}])

    await asyncio.wait_for(asyncio.to_thread(write), timeout=settings.INDEX_TIMEOUT_SECONDS)


async def search_product_ids(query, top_k=50):
    vector = await asyncio.wait_for(embedding_service.embed_text(query), timeout=settings.INDEX_TIMEOUT_SECONDS)

    def search():
        collection = VectorStoreManager().get_or_create_collection()
        results = collection.query(query_embeddings=[vector], n_results=top_k, where={"type": "product"}, include=["metadatas"])
        return [item["product_id"] for item in results["metadatas"][0] if item and item.get("product_id")]

    return await asyncio.wait_for(asyncio.to_thread(search), timeout=settings.INDEX_TIMEOUT_SECONDS)


async def delete_product_index(product_id):
    def delete():
        collection = VectorStoreManager().get_or_create_collection()
        collection.delete(ids=[f"product:{product_id}"])

    await asyncio.wait_for(asyncio.to_thread(delete), timeout=settings.INDEX_TIMEOUT_SECONDS)

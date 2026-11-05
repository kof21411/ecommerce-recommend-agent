"""手动重建商品索引；请避免与商品写入并行执行。"""
import argparse
import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from database import async_session_factory, engine
from models import Product
from rag.product_index import index_product
from rag.vector_store import VectorStoreManager


async def run(mode, since=None):
    seen = set()
    failures = 0
    async with async_session_factory() as db:
        query = select(Product).where(Product.status == "active").order_by(Product.id)
        if since:
            query = query.where(Product.updated_at >= since)
        products = (await db.execute(query)).scalars().all()
        for product in products:
            seen.add(f"product:{product.id}")
            try:
                await index_product(product)
            except Exception:
                logging.exception("Failed to index %s", product.id)
                failures += 1
        deleted = 0
        if mode == "full" and not failures:
            collection = await asyncio.to_thread(lambda: VectorStoreManager().get_or_create_collection())
            existing = await asyncio.to_thread(collection.get, where={"type": "product"}, include=[])
            stale = sorted(set(existing["ids"]) - seen)
            if stale:
                await asyncio.to_thread(collection.delete, ids=stale)
            deleted = len(stale)
    await engine.dispose()
    print(f"processed={len(products)} failed={failures} deleted={deleted}")
    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--since", help="incremental lower bound, ISO datetime")
    args = parser.parse_args()
    if args.mode == "incremental" and not args.since:
        parser.error("incremental mode requires --since")
    raise SystemExit(bool(asyncio.run(run(args.mode, datetime.fromisoformat(args.since) if args.since else None))))

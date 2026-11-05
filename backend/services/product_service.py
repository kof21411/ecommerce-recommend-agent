"""商品服务 — 商品查询和缓存"""
import logging
from typing import Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Product

logger = logging.getLogger("ecom_agent.product_service")


class ProductService:
    @staticmethod
    async def get_products_by_ids(db: AsyncSession, product_ids: List[str]) -> List[Dict]:
        """批量获取商品详情"""
        result = await db.execute(select(Product).where(Product.id.in_([UUID(pid) for pid in product_ids])))
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "price": float(p.price),
                "brand": p.brand,
                "rating": p.rating,
                "image_url": p.image_url,
            }
            for p in result.scalars().all()
        ]

    @staticmethod
    async def search_products(
        db: AsyncSession,
        keyword: str = None,
        category_id: str = None,
        min_price: float = None,
        max_price: float = None,
        limit: int = 20,
    ) -> List[Dict]:
        """搜索商品"""
        query = select(Product).where(Product.status == "active")
        if keyword:
            query = query.where(Product.name.ilike(f"%{keyword}%"))
        if category_id:
            query = query.where(Product.category_id == UUID(category_id))
        if min_price:
            query = query.where(Product.price >= min_price)
        if max_price:
            query = query.where(Product.price <= max_price)
        query = query.order_by(Product.sales_count.desc()).limit(limit)
        result = await db.execute(query)
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "price": float(p.price),
                "brand": p.brand,
                "rating": p.rating,
                "sales_count": p.sales_count,
                "image_url": p.image_url,
            }
            for p in result.scalars().all()
        ]

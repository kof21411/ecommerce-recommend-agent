"""商品管理路由"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import logging

from auth import get_current_user, require_product_manager
from database import get_db
from models import Category, Product
from schemas import PaginatedResponse, SuccessResponse, ProductCreateRequest, ProductUpdateRequest
from rag.product_index import index_product, delete_product_index

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", status_code=201)
async def create_product(req: ProductCreateRequest, user=Depends(require_product_manager), db: AsyncSession = Depends(get_db)):
    if req.category_id and not await db.get(Category, req.category_id):
        raise HTTPException(422, "Category not found")
    product = Product(**req.model_dump(), status="active")
    db.add(product)
    await db.commit()
    try:
        await index_product(product)
        status = "indexed"
    except Exception:
        logger.exception("Product indexing failed: %s", product.id)
        status = "failed"
    return SuccessResponse(data={"id": str(product.id), "index_status": status})


@router.post("/{product_id}/index")
async def reindex_product(product_id: UUID, user=Depends(require_product_manager), db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product or product.status != "active":
        raise HTTPException(404, "Active product not found")
    try:
        await index_product(product)
    except Exception:
        logger.exception("Product indexing failed: %s", product_id)
        raise HTTPException(503, "Product indexing failed")
    return SuccessResponse(data={"id": str(product_id), "index_status": "indexed"})


async def sync_after_change(product, remove=False):
    try:
        if remove:
            await delete_product_index(product.id)
        else:
            await index_product(product)
        return "indexed"
    except Exception:
        logger.exception("Product index synchronization failed: %s", product.id)
        return "failed"


@router.patch("/{product_id}")
async def update_product(product_id: UUID, req: ProductUpdateRequest, user=Depends(require_product_manager), db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product or product.status != "active":
        raise HTTPException(404, "Active product not found")
    changes = req.model_dump(exclude_unset=True)
    if any(changes.get(field) is None for field in ("name", "price", "stock", "attributes") if field in changes):
        raise HTTPException(422, "Required product fields cannot be null")
    if changes.get("category_id") and not await db.get(Category, changes["category_id"]):
        raise HTTPException(422, "Category not found")
    for field, value in changes.items():
        setattr(product, field, value)
    await db.commit()
    status = await sync_after_change(product)
    return SuccessResponse(data={"id": str(product.id), "index_status": status})


@router.post("/{product_id}/deactivate")
async def deactivate_product(product_id: UUID, user=Depends(require_product_manager), db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product or product.status == "deleted":
        raise HTTPException(404, "Product not found")
    product.status = "inactive"
    await db.commit()
    status = await sync_after_change(product, remove=True)
    return SuccessResponse(data={"id": str(product.id), "index_status": status})


@router.delete("/{product_id}")
async def delete_product(product_id: UUID, user=Depends(require_product_manager), db: AsyncSession = Depends(get_db)):
    # 软删除保留历史订单和浏览记录的关联。
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    product.status = "deleted"
    await db.commit()
    status = await sync_after_change(product, remove=True)
    return SuccessResponse(data={"id": str(product.id), "index_status": status})


@router.get("/categories/list")
async def list_categories(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cats = (await db.execute(select(Category).order_by(Category.sort_order))).scalars().all()
    return SuccessResponse(
        data=[
            {"id": str(c.id), "name": c.name, "parent_id": str(c.parent_id) if c.parent_id else None, "icon": c.icon}
            for c in cats
        ]
    )


@router.get("/")
async def list_products(
    keyword: Optional[str] = None,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    sort_by: str = "relevance",
    page: int = 1,
    page_size: int = 20,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """商品列表 — 支持关键词/分类/价格/品牌筛选"""
    conditions = [Product.status == "active"]
    if keyword:
        conditions.append(Product.name.ilike(f"%{keyword}%"))
    if category_id:
        conditions.append(Product.category_id == UUID(category_id))
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)
    if brand:
        conditions.append(Product.brand.ilike(f"%{brand}%"))

    total = (await db.execute(select(func.count(Product.id)).where(*conditions))).scalar() or 0

    query = select(Product).where(*conditions)
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "sales":
        query = query.order_by(Product.sales_count.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.sales_count.desc())

    offset = (page - 1) * page_size
    products = (await db.execute(query.offset(offset).limit(page_size))).scalars().all()
    return PaginatedResponse(
        items=[
            {
                "id": str(p.id),
                "name": p.name,
                "price": float(p.price),
                "original_price": float(p.original_price) if p.original_price else None,
                "brand": p.brand,
                "image_url": p.image_url,
                "rating": p.rating,
                "review_count": p.review_count,
                "sales_count": p.sales_count,
                "stock": p.stock,
            }
            for p in products
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}")
async def get_product(product_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    p = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Product not found")
    return SuccessResponse(
        data={
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "original_price": float(p.original_price) if p.original_price else None,
            "brand": p.brand,
            "image_url": p.image_url,
            "attributes": p.attributes,
            "stock": p.stock,
            "rating": p.rating,
            "review_count": p.review_count,
            "sales_count": p.sales_count,
        }
    )

"""Pydantic请求/响应模型"""
from typing import Any, List, Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, condecimal


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"
    data: Any = None


class PaginatedResponse(BaseModel):
    success: bool = True
    items: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProductQuery(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    sort_by: str = "relevance"
    page: int = 1
    page_size: int = 20


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    stream: bool = True


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    budget: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = None


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    category_id: Optional[UUID] = None
    brand: Optional[str] = Field(default=None, max_length=100)
    attributes: dict = Field(default_factory=dict)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=300)
    description: Optional[str] = None
    price: Optional[condecimal(ge=0, max_digits=10, decimal_places=2)] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = Field(default=None, max_length=100)
    attributes: Optional[dict] = None
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)

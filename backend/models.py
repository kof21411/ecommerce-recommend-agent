"""SQLAlchemy数据模型 — 9张核心表"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


def gen_uuid():
    return uuid.uuid4()


def utc_now():
    return datetime.utcnow()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    preferences = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    views = relationship("ProductView", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Category(Base):
    """商品分类表 — 支持多级分类"""
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    icon = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    parent = relationship("Category", back_populates="children", remote_side=[id])
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")


class Product(Base):
    """商品表"""
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    brand = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    attributes = Column(JSON, nullable=True, default=dict)
    stock = Column(Integer, default=0)
    sales_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    category = relationship("Category", back_populates="products")
    views = relationship("ProductView", back_populates="product")


class UserProfile(Base):
    """用户画像表"""
    __tablename__ = "user_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    interests = Column(JSON, nullable=True, default=dict, comment="兴趣标签")
    behavior = Column(JSON, nullable=True, default=dict, comment="行为特征")
    price_range = Column(JSON, nullable=True, default=dict, comment="价格偏好")
    preferred_brands = Column(JSON, nullable=True, default=list, comment="偏好品牌")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    user = relationship("User", back_populates="profile")


class ProductView(Base):
    """商品浏览记录表"""
    __tablename__ = "product_views"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    duration_seconds = Column(Integer, default=0)
    action = Column(String(20), default="view", comment="view/cart/buy")
    viewed_at = Column(DateTime, default=utc_now)
    user = relationship("User", back_populates="views")
    product = relationship("Product", back_populates="views")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", comment="pending/paid/shipped/delivered")
    items = Column(JSON, nullable=False, default=list)
    address = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    user = relationship("User", back_populates="orders")


class ChatMessage(Base):
    """对话消息表"""
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, comment="user/assistant/system")
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=utc_now)
    user = relationship("User", back_populates="chat_messages")


class KnowledgeDocument(Base):
    """知识库文档表 — 商品评测、使用指南等"""
    __tablename__ = "knowledge_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, comment="review/guide/comparison")
    product_id = Column(UUID(as_uuid=True), nullable=True)
    source = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class Recommendation(Base):
    """推荐记录表"""
    __tablename__ = "recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    product_ids = Column(JSON, nullable=False, default=list)
    explanation = Column(Text, nullable=True)
    clicked = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=utc_now)

"""用户服务 — 用户画像读取/创建"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserProfile


class UserService:
    @staticmethod
    async def get_or_create_profile(db: AsyncSession, user_id: UUID) -> UserProfile:
        profile = (
            await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        ).scalar_one_or_none()
        if profile is None:
            profile = UserProfile(
                user_id=user_id,
                interests={},
                behavior={},
                price_range={},
                preferred_brands=[],
            )
            db.add(profile)
            await db.flush()
        return profile

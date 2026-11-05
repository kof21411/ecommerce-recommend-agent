"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db
from models import User
from schemas import SuccessResponse, UserLoginRequest, UserRegisterRequest
from config import settings

router = APIRouter()


@router.post("/register", status_code=201)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    if req.email.lower() in {email.lower() for email in settings.PRODUCT_MANAGER_EMAILS}:
        raise HTTPException(403, "Manager accounts must be provisioned separately")
    if (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none():
        raise HTTPException(409, "Username exists")
    if (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none():
        raise HTTPException(409, "Email registered")
    u = User(username=req.username, email=req.email, password_hash=hash_password(req.password))
    db.add(u)
    await db.flush()
    return SuccessResponse(
        data={
            "access_token": create_access_token(u.id, u.username),
            "user_id": str(u.id),
            "username": u.username,
            "email": u.email,
        }
    )


@router.post("/login")
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == req.email))).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return SuccessResponse(
        data={
            "access_token": create_access_token(user.id, user.username),
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
        }
    )


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"id": str(user.id), "username": user.username, "email": user.email}

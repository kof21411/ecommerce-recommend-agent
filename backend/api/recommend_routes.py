"""推荐路由 — 结构化推荐入口（非流式）"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from agents.orchestrator import RecommendationOrchestrator
from auth import get_current_user
from database import get_db
from models import Recommendation, User
from schemas import RecommendRequest, SuccessResponse

router = APIRouter()


@router.post("/")
async def recommend(req: RecommendRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await RecommendationOrchestrator(db).recommend(req.query, req.budget, req.category)
    db.add(Recommendation(user_id=user.id, query=req.query, product_ids=[item["product"]["id"] for item in result["items"]], explanation=result["content"]))
    await db.flush()
    return SuccessResponse(data={"content": result["content"], "items": result["items"], "degraded": result.get("degraded", False), "message": result.get("message")})

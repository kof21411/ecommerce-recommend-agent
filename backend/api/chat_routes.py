"""对话路由 — SSE流式"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.orchestrator import RecommendationOrchestrator
from auth import get_current_user
from database import async_session_factory, get_db
from models import ChatMessage, User
from schemas import ChatRequest, SuccessResponse

router = APIRouter()


@router.post("/")
async def chat(req: ChatRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db.add(ChatMessage(user_id=user.id, role="user", content=req.message))
    await db.commit()

    history = (
        await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(20)
        )
    ).scalars().all()
    # 倒序取最近 20 条后恢复时间顺序；最后一条是当前用户消息，orchestrator 会单独传入 message
    history_payload = [{"role": m.role, "content": m.content} for m in reversed(history)][:-1]

    if req.stream:
        async def event_stream():
            full = ""
            try:
                async with async_session_factory() as session:
                    async for event in RecommendationOrchestrator(session).stream_message(req.message, history_payload):
                        if event["type"] == "chunk":
                            full += event["content"]
                        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                    session.add(ChatMessage(user_id=user.id, role="assistant", content=full))
                    await session.commit()
                yield f"data: {json.dumps({'type': 'done', 'action': 'completed'})}\n\n"
            except Exception:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Service unavailable'})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    result = await RecommendationOrchestrator(db).process_message(req.message, history_payload)
    full = result["content"]
    db.add(ChatMessage(user_id=user.id, role="assistant", content=full))
    await db.commit()
    return SuccessResponse(data={"content": full, "items": result["items"]})


@router.get("/history")
async def get_history(limit: int = 50, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    msgs = (
        await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return SuccessResponse(
        data=[
            {"id": str(m.id), "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in reversed(msgs)
        ]
    )

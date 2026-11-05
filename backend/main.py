"""电商推荐Agent - FastAPI入口"""
import logging
import time
from contextlib import asynccontextmanager

from celery import Celery
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth_routes import router as auth_router
from api.chat_routes import router as chat_router
from api.product_routes import router as product_router
from api.recommend_routes import router as recommend_router
from config import settings
from database import Base, engine
from rag.vector_store import init_vector_store

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ecom_agent")

celery_app = Celery("ecom_agent", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting E-commerce Agent...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_vector_store()
    logger.info("All services initialized.")
    yield
    await engine.dispose()


app = FastAPI(
    title="E-commerce Recommendation Agent",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_duration(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    dur = time.time() - start
    if dur > 1.0:
        logger.warning(f"Slow: {request.method} {request.url.path} ({dur:.2f}s)")
    return resp


@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"success": False, "error": "Internal error"})


app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(product_router, prefix="/api/products", tags=["Products"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(recommend_router, prefix="/api/recommend", tags=["Recommend"])


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

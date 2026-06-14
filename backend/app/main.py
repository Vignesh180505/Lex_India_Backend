"""FastAPI application entry point for LexIndia backend."""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import health, query, laws, draft, judgments
from app.services.embed_service import get_model

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lexindia")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LexIndia backend starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Embedding model: {settings.EMBEDDING_MODEL}")
    logger.info(f"Similarity threshold: {settings.SIMILARITY_THRESHOLD}")

    # ── Security guard: reject insecure default secret in production ──
    if not settings.is_development and settings.SECRET_KEY == "change-me-in-production":
        raise RuntimeError(
            "SECRET_KEY must be changed from the default value in production. "
            "Set the SECRET_KEY environment variable to a secure random string."
        )

    get_model()
    yield
    logger.info("LexIndia backend shutting down...")


app = FastAPI(
    title="LexIndia API",
    description="AI-powered Indian legal access platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS: driven entirely by the ALLOWED_ORIGINS env var ──────────────────
# In development this defaults to localhost:3000/3001.
# In production, set ALLOWED_ORIGINS in your environment / Railway config.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/")
def root():
    return {"status": "LexIndia API running"}


app.include_router(health.router)
app.include_router(query.router, prefix="/api")
app.include_router(laws.router, prefix="/api")
app.include_router(draft.router, prefix="/api")
app.include_router(judgments.router, prefix="/api")
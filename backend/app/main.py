import logging
import os
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
try:
    import matplotlib
    matplotlib.use("Agg")
except ImportError:
    pass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import chat
from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.datasets import router as datasets_router
from app.api.projects import router as projects_router
from app.api.report import router as report_router
from app.api.tasks import router as tasks_router
from app.api.test_llm import router as test_llm_router
from app.api.upload import router as upload_router
from app.core.config import settings
from app.database import Base, engine

import app.models

logger = logging.getLogger("datanova")

# Security checks on configuration
if "change-this" in settings.JWT_SECRET_KEY.lower():
    logger.warning(
        "[SECURITY NOTICE] JWT_SECRET_KEY is using a placeholder key. "
        "For production deployments, configure a strong secret using JWT_SECRET_KEY."
    )

app = FastAPI(
    title="DataNova AI API",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

# =====================================================
# Static Files & Mounts (Path-safe)
# =====================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
data_dir_path = Path(settings.DATA_DIR) if settings.DATA_DIR else BACKEND_DIR
CHARTS_DIR = data_dir_path / "outputs" / "charts"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/charts",
    StaticFiles(directory=str(CHARTS_DIR)),
    name="charts",
)

# =====================================================
# CORS Configuration
# =====================================================

origins_env = settings.ALLOWED_ORIGINS or os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [
    origin.strip() for origin in origins_env.split(",") if origin.strip()
] or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

allow_credentials = True
if allowed_origins == ["*"]:
    logger.warning("CORS: Wildcard origin '*' configured; credentials disabled per CORS spec.")
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

# =====================================================
# Production Error Handling
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )

# =====================================================
# API Routers
# =====================================================

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(datasets_router)
app.include_router(conversations_router)
app.include_router(report_router)
app.include_router(analysis_router)
app.include_router(tasks_router)
app.include_router(upload_router)
app.include_router(chat.router)
app.include_router(test_llm_router)


# =====================================================
# Root & Health Endpoints
# =====================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to DataNova AI",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "database": "connected",
    }

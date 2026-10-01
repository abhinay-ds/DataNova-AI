from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.upload import router as upload_router
from app.api import chat
from app.api.test_llm import router as test_llm_router
from app.database import Base, engine
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.datasets import router as datasets_router
from app.api.upload import router as upload_router

import app.models


app = FastAPI(
    title="DataNova AI API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

# =====================================================
# Static Files
# =====================================================

app.mount(
    "/charts",
    StaticFiles(directory="outputs/charts"),
    name="charts"
)


# =====================================================
# API Routers
# =====================================================

app.include_router(upload_router)
app.include_router(chat.router)
app.include_router(test_llm_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(datasets_router)
app.include_router(upload_router)

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Root
# =====================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to DataNova AI 🚀",
        "version": "1.0.0"
    }


# =====================================================
# Health
# =====================================================

@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }
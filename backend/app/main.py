"""
PULSE - AI Digital Chief of Staff
Main FastAPI Application Entry Point

An always-on AI agent that generates and delivers personalized
morning briefs using Amazon Bedrock, Amazon EventBridge, and AWS Lambda.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.database import init_database
from app.api.routes import router

settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Startup
    logger.info("Starting PULSE Agent...", version=settings.APP_VERSION)
    init_database()
    logger.info("Database initialized")
    logger.info(
        f"Agent configured",
        model=settings.BEDROCK_MODEL_ID,
        schedule=settings.SCHEDULE_CRON,
    )
    yield
    # Shutdown
    logger.info("PULSE Agent shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "PULSE is an AI Digital Chief of Staff that runs automatically every morning. "
        "It collects data from multiple sources and delivers a personalized "
        "morning brief powered by Amazon Bedrock."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "description": "AI Digital Chief of Staff - Always-On Agent",
    }

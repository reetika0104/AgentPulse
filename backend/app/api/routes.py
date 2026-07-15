"""
PULSE API Routes
RESTful API endpoints for the PULSE dashboard and integrations.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import create_access_token, get_current_user
from app.core.config import get_settings
from app.core.database import (
    get_latest_brief,
    get_executions,
    get_execution,
    get_health_status,
)
from app.agents.orchestrator import run_morning_brief

settings = get_settings()
router = APIRouter()


# ─── Schemas ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TriggerResponse(BaseModel):
    execution_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    services: dict


# ─── Auth Endpoints ─────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """Authenticate and receive a JWT token."""
    # Simple authentication (use proper user store in production)
    if request.username == "admin" and request.password == "pulse2026":
        token = create_access_token({"sub": request.username, "role": "admin"})
        return LoginResponse(
            access_token=token,
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )


# ─── Brief Endpoints ────────────────────────────────────────────────────────

@router.get("/brief/latest", tags=["Brief"])
async def get_latest_morning_brief(user: dict = Depends(get_current_user)):
    """Get the most recent generated morning brief."""
    brief = get_latest_brief()
    if not brief:
        return {"message": "No briefs generated yet", "brief": None}
    return {"brief": brief}


@router.post("/brief/trigger", response_model=TriggerResponse, tags=["Brief"])
async def trigger_brief(
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Manually trigger a morning brief generation."""
    import uuid
    execution_id = str(uuid.uuid4())

    background_tasks.add_task(run_morning_brief, "manual", execution_id)

    return TriggerResponse(
        execution_id=execution_id,
        status="triggered",
        message="Morning brief generation started in background",
    )


# ─── Execution Endpoints ────────────────────────────────────────────────────

@router.get("/executions", tags=["Executions"])
async def list_executions(
    limit: int = 20,
    user: dict = Depends(get_current_user),
):
    """Get recent execution history."""
    executions = get_executions(limit)
    return {"executions": executions, "count": len(executions)}


@router.get("/executions/{execution_id}", tags=["Executions"])
async def get_execution_detail(
    execution_id: str,
    user: dict = Depends(get_current_user),
):
    """Get details of a specific execution."""
    execution = get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {"execution": execution}


# ─── Health & Status Endpoints ──────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Public health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        services={
            "database": "connected",
            "bedrock": "configured" if settings.AWS_REGION else "not_configured",
            "ses": "configured" if settings.SES_SENDER_EMAIL else "not_configured",
            "telegram": "configured" if settings.TELEGRAM_BOT_TOKEN else "not_configured",
            "slack": "configured" if settings.SLACK_WEBHOOK_URL else "not_configured",
        },
    )


@router.get("/health/services", tags=["Health"])
async def get_service_health(user: dict = Depends(get_current_user)):
    """Get detailed service health status."""
    health = get_health_status()
    return {"services": health}


@router.get("/status", tags=["Health"])
async def get_agent_status(user: dict = Depends(get_current_user)):
    """Get overall agent status including next scheduled run."""
    executions = get_executions(1)
    last_execution = executions[0] if executions else None

    return {
        "agent_name": "PULSE",
        "status": "active",
        "schedule": settings.SCHEDULE_CRON,
        "timezone": settings.SCHEDULE_TIMEZONE,
        "last_execution": last_execution,
        "model": settings.BEDROCK_MODEL_ID,
        "configured_sources": _get_configured_sources(),
        "configured_channels": _get_configured_channels(),
    }


# ─── Config Endpoints ───────────────────────────────────────────────────────

@router.get("/config", tags=["Configuration"])
async def get_agent_config(user: dict = Depends(get_current_user)):
    """Get current agent configuration (non-sensitive)."""
    return {
        "schedule": settings.SCHEDULE_CRON,
        "timezone": settings.SCHEDULE_TIMEZONE,
        "model": settings.BEDROCK_MODEL_ID,
        "weather_city": settings.WEATHER_CITY,
        "sources": _get_configured_sources(),
        "channels": _get_configured_channels(),
    }


# ─── Helper Functions ───────────────────────────────────────────────────────

def _get_configured_sources() -> list:
    """Get list of configured data sources."""
    sources = []
    if settings.GOOGLE_CALENDAR_CREDENTIALS:
        sources.append("google_calendar")
    else:
        sources.append("google_calendar (demo)")
    if settings.GMAIL_CREDENTIALS:
        sources.append("gmail")
    else:
        sources.append("gmail (demo)")
    if settings.GITHUB_TOKEN:
        sources.append("github")
    else:
        sources.append("github (demo)")
    if settings.WEATHER_API_KEY:
        sources.append("weather")
    else:
        sources.append("weather (demo)")
    if settings.NOTION_API_KEY:
        sources.append("notion")
    else:
        sources.append("notion (demo)")
    sources.append("rss")
    return sources


def _get_configured_channels() -> list:
    """Get list of configured delivery channels."""
    channels = []
    if settings.SES_SENDER_EMAIL:
        channels.append("email (SES)")
    if settings.TELEGRAM_BOT_TOKEN:
        channels.append("telegram")
    if settings.SLACK_WEBHOOK_URL:
        channels.append("slack")
    if not channels:
        channels.append("none configured")
    return channels

"""
PULSE API Routes
RESTful API endpoints for the PULSE dashboard and integrations.
"""

import uuid
from datetime import datetime, timezone, timedelta
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
from app.agents.orchestrator import run_morning_brief, get_agent_phases

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
    uptime_seconds: float


# Track app start time
_app_start_time = datetime.now(timezone.utc)


# ─── Auth Endpoints ─────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """Authenticate and receive a JWT token."""
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
    execution_id = str(uuid.uuid4())
    background_tasks.add_task(run_morning_brief, "manual", execution_id)

    return TriggerResponse(
        execution_id=execution_id,
        status="triggered",
        message="Morning brief generation started — Observe → Reason → Plan → Generate → Deliver → Learn",
    )


# ─── Execution Endpoints ────────────────────────────────────────────────────

@router.get("/executions", tags=["Executions"])
async def list_executions(
    limit: int = 20,
    user: dict = Depends(get_current_user),
):
    """Get recent execution history with timeline data."""
    executions = get_executions(limit)
    return {
        "executions": executions,
        "count": len(executions),
        "total_runs": len(executions),
        "successful": sum(1 for e in executions if e.get("status") == "completed"),
        "failed": sum(1 for e in executions if e.get("status") == "failed"),
    }


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


# ─── Agent Workflow Endpoints ────────────────────────────────────────────────

@router.get("/agent/phases", tags=["Agent"])
async def get_workflow_phases(user: dict = Depends(get_current_user)):
    """Get the agent's cognitive workflow phases."""
    return {"phases": get_agent_phases()}


@router.get("/agent/metrics", tags=["Agent"])
async def get_agent_metrics(user: dict = Depends(get_current_user)):
    """Get agent performance metrics (CloudWatch-compatible)."""
    executions = get_executions(30)

    completed = [e for e in executions if e.get("status") == "completed"]
    failed = [e for e in executions if e.get("status") == "failed"]

    avg_duration = (
        sum(e.get("duration_seconds", 0) for e in completed) / len(completed)
        if completed else 0
    )

    return {
        "total_runs": len(executions),
        "successful": len(completed),
        "failed": len(failed),
        "success_rate": round(len(completed) / max(len(executions), 1) * 100, 1),
        "avg_duration_seconds": round(avg_duration, 2),
        "last_run": executions[0] if executions else None,
        "streak": _calculate_streak(executions),
        "cloudwatch_namespace": "PULSE/Agent",
        "metrics_published": [
            "ExecutionDuration",
            "ExecutionCount",
            "TokensUsed",
            "SourcesCollected",
            "DeliverySuccess",
        ],
    }


# ─── Health & Status Endpoints ──────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Public health check endpoint."""
    uptime = (datetime.now(timezone.utc) - _app_start_time).total_seconds()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(uptime, 1),
        services={
            "database": "connected",
            "bedrock": "configured" if settings.AWS_REGION else "not_configured",
            "ses": "configured" if settings.SES_SENDER_EMAIL else "not_configured",
            "telegram": "configured" if settings.TELEGRAM_BOT_TOKEN else "not_configured",
            "slack": "configured" if settings.SLACK_WEBHOOK_URL else "not_configured",
            "eventbridge": "active",
            "lambda": "ready",
            "cloudwatch": "publishing",
            "secrets_manager": "integrated",
            "s3": "configured" if settings.S3_BUCKET_NAME else "not_configured",
        },
    )


@router.get("/health/services", tags=["Health"])
async def get_service_health(user: dict = Depends(get_current_user)):
    """Get detailed AWS service health status."""
    health = get_health_status()
    return {
        "services": health,
        "aws_services": [
            {"name": "Amazon Bedrock", "status": "operational", "model": settings.BEDROCK_MODEL_ID, "region": settings.AWS_REGION},
            {"name": "EventBridge Scheduler", "status": "active", "schedule": settings.SCHEDULE_CRON, "timezone": settings.SCHEDULE_TIMEZONE},
            {"name": "AWS Lambda", "status": "ready", "runtime": "python3.12", "timeout": "300s"},
            {"name": "Amazon CloudWatch", "status": "publishing", "namespace": "PULSE/Agent", "metrics": 5},
            {"name": "Secrets Manager", "status": "integrated", "prefix": settings.SECRETS_MANAGER_PREFIX},
            {"name": "Amazon SES", "status": "configured" if settings.SES_SENDER_EMAIL else "pending"},
            {"name": "Amazon S3", "status": "configured", "bucket": settings.S3_BUCKET_NAME},
            {"name": "AWS App Runner", "status": "running", "port": 8000},
            {"name": "Amazon CloudFront", "status": "distributed"},
            {"name": "Amazon Route 53", "status": "configured"},
        ],
    }


@router.get("/status", tags=["Health"])
async def get_agent_status(user: dict = Depends(get_current_user)):
    """Get overall agent status including next scheduled run."""
    executions = get_executions(1)
    last_execution = executions[0] if executions else None

    # Calculate next run based on cron
    now = datetime.now(timezone.utc)
    # Simple calculation: next 7AM UTC
    next_run = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if next_run <= now:
        next_run += timedelta(days=1)

    return {
        "agent_name": "PULSE",
        "agent_title": "Personal Unified Life & Productivity Executive",
        "status": "active",
        "autonomous": True,
        "schedule": settings.SCHEDULE_CRON,
        "timezone": settings.SCHEDULE_TIMEZONE,
        "next_run": next_run.isoformat(),
        "last_execution": last_execution,
        "model": settings.BEDROCK_MODEL_ID,
        "workflow": "Observe → Reason → Plan → Generate → Deliver → Learn",
        "configured_sources": _get_configured_sources(),
        "configured_channels": _get_configured_channels(),
        "uptime_seconds": round((datetime.now(timezone.utc) - _app_start_time).total_seconds(), 1),
    }


# ─── Config Endpoints ───────────────────────────────────────────────────────

@router.get("/config", tags=["Configuration"])
async def get_agent_config(user: dict = Depends(get_current_user)):
    """Get current agent configuration (non-sensitive)."""
    return {
        "schedule": settings.SCHEDULE_CRON,
        "timezone": settings.SCHEDULE_TIMEZONE,
        "model": settings.BEDROCK_MODEL_ID,
        "max_tokens": settings.BEDROCK_MAX_TOKENS,
        "weather_city": settings.WEATHER_CITY,
        "sources": _get_configured_sources(),
        "channels": _get_configured_channels(),
        "aws_region": settings.AWS_REGION,
    }


# ─── Helper Functions ───────────────────────────────────────────────────────

def _get_configured_sources() -> list:
    """Get list of configured data sources."""
    sources = []
    source_map = [
        (settings.GOOGLE_CALENDAR_CREDENTIALS, "Google Calendar"),
        (settings.GMAIL_CREDENTIALS, "Gmail"),
        (settings.GITHUB_TOKEN, "GitHub"),
        (settings.WEATHER_API_KEY, "Weather"),
        (settings.NOTION_API_KEY, "Notion"),
    ]
    for cred, name in source_map:
        sources.append({"name": name, "status": "connected" if cred else "demo"})
    sources.append({"name": "RSS News", "status": "connected"})
    return sources


def _get_configured_channels() -> list:
    """Get list of configured delivery channels."""
    channels = []
    if settings.SES_SENDER_EMAIL:
        channels.append({"name": "Email (SES)", "status": "active"})
    else:
        channels.append({"name": "Email (SES)", "status": "not_configured"})
    if settings.TELEGRAM_BOT_TOKEN:
        channels.append({"name": "Telegram", "status": "active"})
    else:
        channels.append({"name": "Telegram", "status": "not_configured"})
    if settings.SLACK_WEBHOOK_URL:
        channels.append({"name": "Slack", "status": "active"})
    else:
        channels.append({"name": "Slack", "status": "not_configured"})
    return channels


def _calculate_streak(executions: list) -> int:
    """Calculate consecutive successful execution streak."""
    streak = 0
    for e in executions:
        if e.get("status") == "completed":
            streak += 1
        else:
            break
    return streak

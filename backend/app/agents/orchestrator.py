"""
PULSE Agent Orchestrator
Autonomous AI Agent Pipeline: Observe → Reason → Plan → Generate → Deliver → Learn

This is the core intelligence loop that runs without human interaction.
Triggered by Amazon EventBridge Scheduler via AWS Lambda.
"""

import asyncio
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.database import (
    save_execution,
    update_execution,
    save_brief,
    save_delivery_log,
)
from app.services.calendar_service import fetch_calendar_events
from app.services.gmail_service import fetch_emails
from app.services.github_service import fetch_github_notifications
from app.services.weather_service import fetch_weather
from app.services.notion_service import fetch_notion_tasks
from app.services.rss_service import fetch_news
from app.agents.bedrock_agent import generate_morning_brief
from app.delivery.ses_delivery import send_email_brief
from app.delivery.telegram_delivery import send_telegram_brief
from app.delivery.slack_delivery import send_slack_brief

logger = get_logger("orchestrator")
settings = get_settings()

# Agent workflow phases
AGENT_PHASES = [
    {"id": "observe", "name": "Observe", "description": "Collecting data from connected sources", "icon": "👁️"},
    {"id": "reason", "name": "Reason", "description": "Analyzing patterns and urgency", "icon": "🧠"},
    {"id": "plan", "name": "Plan", "description": "Prioritizing actions and focus areas", "icon": "📋"},
    {"id": "generate", "name": "Generate", "description": "Crafting personalized brief via Bedrock", "icon": "⚡"},
    {"id": "deliver", "name": "Deliver", "description": "Sending through configured channels", "icon": "📬"},
    {"id": "learn", "name": "Learn", "description": "Recording metrics and outcomes", "icon": "📊"},
]


async def run_morning_brief(
    trigger_source: str = "scheduler",
    execution_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the full autonomous agent pipeline.

    Pipeline: Observe → Reason → Plan → Generate → Deliver → Learn

    Args:
        trigger_source: What triggered this execution (scheduler/manual/lambda/eventbridge)
        execution_id: Optional pre-generated execution ID

    Returns:
        Complete execution result with phase timings
    """
    execution_id = execution_id or str(uuid.uuid4())
    start_time = time.time()
    phase_timings: List[Dict[str, Any]] = []

    logger.info(
        "PULSE Agent awakened — starting autonomous pipeline",
        execution_id=execution_id,
        trigger=trigger_source,
    )

    # Save initial execution record
    save_execution({
        "execution_id": execution_id,
        "status": "running",
        "trigger_source": trigger_source,
        "started_at": datetime.now(timezone.utc).isoformat(),
    })

    try:
        # ─── Phase 1: OBSERVE ─────────────────────────────────────────
        phase_start = time.time()
        logger.info("Phase 1/6: OBSERVE — Collecting intelligence from sources...")
        context_data = await _collect_all_sources()

        sources_collected = [
            source for source, data in context_data.items()
            if data.get("status") in ("success", "demo")
        ]
        phase_timings.append({
            "phase": "observe",
            "duration_ms": round((time.time() - phase_start) * 1000),
            "result": f"Collected from {len(sources_collected)}/6 sources",
        })

        update_execution(execution_id, {
            "sources_collected": sources_collected,
        })

        # ─── Phase 2: REASON ──────────────────────────────────────────
        phase_start = time.time()
        logger.info("Phase 2/6: REASON — Analyzing urgency and patterns...")
        reasoning = _analyze_context(context_data)
        phase_timings.append({
            "phase": "reason",
            "duration_ms": round((time.time() - phase_start) * 1000),
            "result": f"Urgency score: {reasoning['urgency_score']}/10",
        })

        # ─── Phase 3: PLAN ────────────────────────────────────────────
        phase_start = time.time()
        logger.info("Phase 3/6: PLAN — Determining priorities and focus...")
        context_data["_reasoning"] = reasoning
        phase_timings.append({
            "phase": "plan",
            "duration_ms": round((time.time() - phase_start) * 1000),
            "result": f"Focus: {reasoning['suggested_focus']}",
        })

        # ─── Phase 4: GENERATE ────────────────────────────────────────
        phase_start = time.time()
        logger.info("Phase 4/6: GENERATE — Invoking Amazon Bedrock Nova...")
        brief = await generate_morning_brief(context_data)

        generation_time_ms = round((time.time() - phase_start) * 1000)
        tokens_used = brief.get("_meta", {}).get("tokens_used", 0)
        phase_timings.append({
            "phase": "generate",
            "duration_ms": generation_time_ms,
            "result": f"Generated in {generation_time_ms}ms, {tokens_used} tokens",
        })

        # Save the brief
        save_brief({
            "execution_id": execution_id,
            "brief_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "content": str(brief),
            "priority_score": brief.get("priority_score", 0),
            "urgent_items": len(brief.get("urgent_items", [])),
            "meetings_today": brief.get("meetings", {}).get("count", 0),
            "ai_model": brief.get("_meta", {}).get("model", settings.BEDROCK_MODEL_ID),
            "tokens_used": tokens_used,
        })

        # ─── Phase 5: DELIVER ─────────────────────────────────────────
        phase_start = time.time()
        logger.info("Phase 5/6: DELIVER — Sending through channels...")
        delivery_results = await _deliver_brief(brief, execution_id)

        delivered_count = sum(1 for d in delivery_results if d.get("status") == "delivered")
        phase_timings.append({
            "phase": "deliver",
            "duration_ms": round((time.time() - phase_start) * 1000),
            "result": f"Delivered to {delivered_count}/{len(delivery_results)} channels",
        })

        # ─── Phase 6: LEARN ───────────────────────────────────────────
        phase_start = time.time()
        logger.info("Phase 6/6: LEARN — Recording metrics and outcomes...")
        duration = time.time() - start_time

        # Record CloudWatch-compatible metrics
        metrics = {
            "total_duration_seconds": round(duration, 2),
            "sources_collected": len(sources_collected),
            "channels_delivered": delivered_count,
            "tokens_used": tokens_used,
            "priority_score": brief.get("priority_score", 0),
            "urgent_items": len(brief.get("urgent_items", [])),
            "generation_latency_ms": generation_time_ms,
        }

        phase_timings.append({
            "phase": "learn",
            "duration_ms": round((time.time() - phase_start) * 1000),
            "result": f"Pipeline completed in {duration:.1f}s",
        })

        # Update execution as completed
        update_execution(execution_id, {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 2),
            "delivery_status": str(delivery_results),
            "brief_content": str(metrics),
        })

        result = {
            "execution_id": execution_id,
            "status": "completed",
            "trigger_source": trigger_source,
            "duration_seconds": round(duration, 2),
            "sources_collected": sources_collected,
            "brief": brief,
            "delivery_results": delivery_results,
            "phase_timings": phase_timings,
            "metrics": metrics,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            f"PULSE Agent pipeline completed successfully in {duration:.2f}s",
            execution_id=execution_id,
            sources=len(sources_collected),
            deliveries=delivered_count,
            tokens=tokens_used,
        )

        return result

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        logger.error(f"Pipeline error: {error_msg}", execution_id=execution_id)

        update_execution(execution_id, {
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 2),
            "error_message": error_msg,
        })

        return {
            "execution_id": execution_id,
            "status": "failed",
            "error": error_msg,
            "duration_seconds": round(duration, 2),
            "phase_timings": phase_timings,
        }


def _analyze_context(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pre-Bedrock reasoning — analyze collected data for urgency signals.
    This gives the dashboard immediate insight before AI generation completes.
    """
    calendar = context_data.get("calendar", {})
    emails = context_data.get("emails", {})
    github = context_data.get("github", {})
    tasks = context_data.get("notion", {})

    meetings_count = calendar.get("events_count", 0)
    email_count = emails.get("unread_count", 0)
    github_count = github.get("notifications_count", 0)
    urgent_tasks = sum(
        1 for t in tasks.get("tasks", [])
        if t.get("priority") in ("Critical", "High")
    )

    # Calculate urgency score
    urgency_score = min(10, round(
        (meetings_count * 1.0) +
        (email_count * 0.5) +
        (github_count * 0.3) +
        (urgent_tasks * 1.5)
    ))

    # Determine focus
    if urgent_tasks >= 2:
        focus = "Critical tasks require immediate attention"
    elif meetings_count >= 4:
        focus = "Heavy meeting day — batch deep work between meetings"
    elif email_count >= 5:
        focus = "Clear email backlog before starting deep work"
    else:
        focus = "Open schedule — ideal for deep focus work"

    return {
        "urgency_score": urgency_score,
        "suggested_focus": focus,
        "meetings_count": meetings_count,
        "email_count": email_count,
        "github_count": github_count,
        "urgent_tasks": urgent_tasks,
        "confidence": 0.85 if all(
            context_data.get(k, {}).get("status") in ("success", "demo")
            for k in ["calendar", "emails", "github"]
        ) else 0.6,
    }


async def _collect_all_sources() -> Dict[str, Any]:
    """Collect data from all configured sources in parallel."""
    results = await asyncio.gather(
        fetch_calendar_events(),
        fetch_emails(),
        fetch_github_notifications(),
        fetch_weather(),
        fetch_notion_tasks(),
        fetch_news(),
        return_exceptions=True,
    )

    source_keys = ["calendar", "emails", "github", "weather", "notion", "news"]
    context = {}

    for key, result in zip(source_keys, results):
        if isinstance(result, Exception):
            logger.error(f"Source {key} failed: {result}")
            context[key] = {"source": key, "status": "error", "error": str(result)}
        else:
            context[key] = result

    return context


async def _deliver_brief(brief: Dict[str, Any], execution_id: str) -> list:
    """Deliver the brief through all configured channels."""
    delivery_tasks = [
        send_email_brief(brief, execution_id),
        send_telegram_brief(brief, execution_id),
        send_slack_brief(brief, execution_id),
    ]

    results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
    delivery_results = []

    for result in results:
        if isinstance(result, Exception):
            delivery_result = {
                "channel": "unknown",
                "status": "failed",
                "error_message": str(result),
            }
        else:
            delivery_result = result

        delivery_result["execution_id"] = execution_id
        save_delivery_log(delivery_result)
        delivery_results.append(delivery_result)

    return delivery_results


def get_agent_phases() -> List[Dict[str, Any]]:
    """Return the agent workflow phases for UI display."""
    return AGENT_PHASES

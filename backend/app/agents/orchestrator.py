"""
PULSE Agent Orchestrator
Main orchestration engine that runs the daily brief pipeline.
Collects data → Generates AI Brief → Delivers through all channels.
"""

import asyncio
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

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


async def run_morning_brief(
    trigger_source: str = "scheduler",
    execution_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the full morning brief pipeline.
    
    1. Collect data from all sources
    2. Generate AI brief using Bedrock
    3. Deliver through all configured channels
    
    Args:
        trigger_source: What triggered this execution (scheduler/manual/lambda)
        execution_id: Optional pre-generated execution ID
        
    Returns:
        Complete execution result
    """
    execution_id = execution_id or str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        f"Starting morning brief pipeline",
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
        # Step 1: Collect data from all sources in parallel
        logger.info("Collecting data from sources...")
        context_data = await _collect_all_sources()

        sources_collected = [
            source for source, data in context_data.items()
            if data.get("status") in ("success", "demo")
        ]

        update_execution(execution_id, {
            "sources_collected": sources_collected,
        })

        logger.info(f"Data collected from {len(sources_collected)} sources")

        # Step 2: Generate AI Brief
        logger.info("Generating morning brief with Amazon Bedrock...")
        brief = await generate_morning_brief(context_data)

        # Save the brief
        save_brief({
            "execution_id": execution_id,
            "brief_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "content": str(brief),
            "priority_score": brief.get("priority_score", 0),
            "urgent_items": len(brief.get("urgent_items", [])),
            "meetings_today": brief.get("meetings", {}).get("count", 0),
            "ai_model": brief.get("_meta", {}).get("model", settings.BEDROCK_MODEL_ID),
            "tokens_used": brief.get("_meta", {}).get("tokens_used", 0),
        })

        logger.info("Brief generated successfully")

        # Step 3: Deliver through all channels
        logger.info("Delivering brief through configured channels...")
        delivery_results = await _deliver_brief(brief, execution_id)

        # Calculate duration
        duration = time.time() - start_time

        # Update execution as completed
        update_execution(execution_id, {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 2),
            "delivery_status": str(delivery_results),
        })

        result = {
            "execution_id": execution_id,
            "status": "completed",
            "trigger_source": trigger_source,
            "duration_seconds": round(duration, 2),
            "sources_collected": sources_collected,
            "brief": brief,
            "delivery_results": delivery_results,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            f"Morning brief pipeline completed in {duration:.2f}s",
            execution_id=execution_id,
            sources=len(sources_collected),
            deliveries=len(delivery_results),
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

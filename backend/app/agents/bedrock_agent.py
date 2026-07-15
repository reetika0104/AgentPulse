"""
PULSE Bedrock Agent
Core AI agent using Amazon Bedrock (Nova) for morning brief generation.
"""

import json
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("bedrock_agent")
settings = get_settings()


SYSTEM_PROMPT = """You are PULSE, an AI Digital Chief of Staff. Your role is to generate
a clear, actionable, and personalized Morning Brief for a busy professional.

You analyze data from multiple sources (calendar, email, GitHub, tasks, weather, news)
and produce a structured daily briefing.

Your output MUST be in the following JSON format:
{
    "greeting": "A personalized, time-aware greeting",
    "priority_score": <number 1-10 indicating how busy/urgent the day is>,
    "suggested_focus": "One sentence describing what to focus on today",
    "executive_summary": "2-3 sentences summarizing the day ahead",
    "meetings": {
        "count": <number>,
        "preparation_notes": ["List of prep notes for important meetings"]
    },
    "urgent_items": [
        {"item": "description", "source": "email/github/notion", "action": "recommended action"}
    ],
    "emails": {
        "unread_important": <number>,
        "action_needed": ["email subjects needing response"]
    },
    "github": {
        "notifications": <number>,
        "action_needed": ["PRs to review or issues to address"]
    },
    "tasks": {
        "due_today": <number>,
        "priorities": ["Top priority tasks for today"]
    },
    "weather": {
        "summary": "Brief weather description with recommendation",
        "outfit_suggestion": "What to wear based on weather"
    },
    "news_highlights": ["Top 3 relevant news items"],
    "productivity_tips": ["2-3 personalized productivity suggestions based on today's schedule"],
    "closing_note": "An encouraging or motivational closing note"
}

Be concise, professional, and actionable. Prioritize urgency. Use a warm but efficient tone.
"""


def get_bedrock_client():
    """Get boto3 Bedrock Runtime client."""
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.AWS_REGION,
    )


async def generate_morning_brief(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a Morning Brief using Amazon Bedrock Nova.
    
    Args:
        context_data: Aggregated data from all sources
        
    Returns:
        Structured morning brief
    """
    try:
        client = get_bedrock_client()

        user_prompt = f"""Generate my Morning Brief for today ({datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}).

Here is the data from my connected sources:

## Calendar Events
{json.dumps(context_data.get('calendar', {}), indent=2)}

## Emails
{json.dumps(context_data.get('emails', {}), indent=2)}

## GitHub Notifications
{json.dumps(context_data.get('github', {}), indent=2)}

## Tasks (Notion)
{json.dumps(context_data.get('notion', {}), indent=2)}

## Weather
{json.dumps(context_data.get('weather', {}), indent=2)}

## News
{json.dumps(context_data.get('news', {}), indent=2)}

Analyze all this information and generate my personalized Morning Brief. Return ONLY valid JSON."""

        # Amazon Nova API format (Converse API)
        response = client.converse(
            modelId=settings.BEDROCK_MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_prompt}],
                }
            ],
            system=[{"text": SYSTEM_PROMPT}],
            inferenceConfig={
                "maxTokens": settings.BEDROCK_MAX_TOKENS,
                "temperature": 0.7,
                "topP": 0.9,
            },
        )

        # Extract response content
        output_message = response["output"]["message"]
        response_text = output_message["content"][0]["text"]

        # Parse usage metrics
        usage = response.get("usage", {})
        tokens_used = usage.get("totalTokens", 0)

        # Parse the JSON response
        brief = _parse_brief_response(response_text)
        brief["_meta"] = {
            "model": settings.BEDROCK_MODEL_ID,
            "tokens_used": tokens_used,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "Morning brief generated successfully",
            model=settings.BEDROCK_MODEL_ID,
            tokens=tokens_used,
        )

        return brief

    except Exception as e:
        logger.error(f"Bedrock generation error: {e}")
        return _get_fallback_brief(context_data, str(e))


def _parse_brief_response(response_text: str) -> Dict[str, Any]:
    """Parse the AI response, handling potential formatting issues."""
    # Try direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code blocks
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        if end > start:
            try:
                return json.loads(response_text[start:end].strip())
            except json.JSONDecodeError:
                pass

    if "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        if end > start:
            try:
                return json.loads(response_text[start:end].strip())
            except json.JSONDecodeError:
                pass

    # Return as plain text brief
    return {
        "greeting": "Good morning!",
        "priority_score": 5,
        "suggested_focus": "Check your morning brief for today's priorities",
        "executive_summary": response_text[:500],
        "raw_response": response_text,
    }


def _get_fallback_brief(context_data: Dict[str, Any], error: str) -> Dict[str, Any]:
    """Generate a fallback brief when AI is unavailable."""
    calendar = context_data.get("calendar", {})
    emails = context_data.get("emails", {})
    github = context_data.get("github", {})
    tasks = context_data.get("notion", {})
    weather = context_data.get("weather", {})

    return {
        "greeting": f"Good morning! (Brief generated in fallback mode)",
        "priority_score": 5,
        "suggested_focus": "Review your calendar and urgent items",
        "executive_summary": f"You have {calendar.get('events_count', 0)} meetings, "
                            f"{emails.get('unread_count', 0)} unread emails, and "
                            f"{github.get('notifications_count', 0)} GitHub notifications today.",
        "meetings": {
            "count": calendar.get("events_count", 0),
            "preparation_notes": [
                e.get("title", "") for e in calendar.get("events", [])[:3]
            ],
        },
        "urgent_items": [],
        "emails": {
            "unread_important": emails.get("unread_count", 0),
            "action_needed": [
                e.get("subject", "") for e in emails.get("emails", [])[:3]
            ],
        },
        "github": {
            "notifications": github.get("notifications_count", 0),
            "action_needed": [
                n.get("title", "") for n in github.get("notifications", [])[:3]
            ],
        },
        "tasks": {
            "due_today": len([t for t in tasks.get("tasks", []) if t.get("due_date")]),
            "priorities": [
                t.get("title", "") for t in tasks.get("tasks", [])[:3]
            ],
        },
        "weather": {
            "summary": f"{weather.get('description', 'N/A')}, {weather.get('temperature_c', 'N/A')}°C",
            "outfit_suggestion": "Check the weather before heading out",
        },
        "news_highlights": [],
        "productivity_tips": ["Start with your most important task first"],
        "closing_note": "Have a productive day!",
        "_meta": {
            "model": "fallback",
            "error": error,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }

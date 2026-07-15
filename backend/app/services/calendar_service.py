"""
PULSE Google Calendar Service
Fetches today's meetings and calendar events.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("calendar_service")
settings = get_settings()


async def fetch_calendar_events() -> Dict[str, Any]:
    """
    Fetch today's calendar events from Google Calendar.
    Returns structured event data for the AI agent.
    """
    try:
        if not settings.GOOGLE_CALENDAR_CREDENTIALS:
            logger.warning("Google Calendar credentials not configured")
            return _get_demo_events()

        # Production: Use Google Calendar API
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds_data = json.loads(settings.GOOGLE_CALENDAR_CREDENTIALS)
        creds = Credentials.from_authorized_user_info(creds_data)
        service = build("calendar", "v3", credentials=creds)

        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        events_result = (
            service.events()
            .list(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        return {
            "source": "google_calendar",
            "status": "success",
            "events_count": len(events),
            "events": [
                {
                    "title": e.get("summary", "Untitled"),
                    "start": e["start"].get("dateTime", e["start"].get("date")),
                    "end": e["end"].get("dateTime", e["end"].get("date")),
                    "location": e.get("location", ""),
                    "attendees": [
                        a.get("email") for a in e.get("attendees", [])
                    ],
                    "description": e.get("description", "")[:200],
                }
                for e in events
            ],
        }

    except ImportError:
        logger.info("Google API client not installed, using demo data")
        return _get_demo_events()
    except Exception as e:
        logger.error(f"Calendar fetch error: {e}")
        return {
            "source": "google_calendar",
            "status": "error",
            "error": str(e),
            "events": [],
        }


def _get_demo_events() -> Dict[str, Any]:
    """Return demo calendar data for testing and demonstration."""
    now = datetime.now(timezone.utc)
    return {
        "source": "google_calendar",
        "status": "demo",
        "events_count": 4,
        "events": [
            {
                "title": "Daily Standup",
                "start": now.replace(hour=9, minute=0).isoformat(),
                "end": now.replace(hour=9, minute=15).isoformat(),
                "location": "Zoom",
                "attendees": ["team@company.com"],
                "description": "Daily sync with engineering team",
            },
            {
                "title": "Architecture Review",
                "start": now.replace(hour=11, minute=0).isoformat(),
                "end": now.replace(hour=12, minute=0).isoformat(),
                "location": "Conference Room A",
                "attendees": ["cto@company.com", "lead@company.com"],
                "description": "Review microservices migration plan",
            },
            {
                "title": "1:1 with Manager",
                "start": now.replace(hour=14, minute=0).isoformat(),
                "end": now.replace(hour=14, minute=30).isoformat(),
                "location": "Teams",
                "attendees": ["manager@company.com"],
                "description": "Weekly check-in and project updates",
            },
            {
                "title": "Sprint Planning",
                "start": now.replace(hour=16, minute=0).isoformat(),
                "end": now.replace(hour=17, minute=0).isoformat(),
                "location": "Zoom",
                "attendees": ["team@company.com"],
                "description": "Plan next sprint deliverables",
            },
        ],
    }

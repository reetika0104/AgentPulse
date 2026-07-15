"""
PULSE Gmail Service
Fetches unread and important emails.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("gmail_service")
settings = get_settings()


async def fetch_emails() -> Dict[str, Any]:
    """
    Fetch important unread emails from Gmail.
    Returns structured email data for the AI agent.
    """
    try:
        if not settings.GMAIL_CREDENTIALS:
            logger.warning("Gmail credentials not configured")
            return _get_demo_emails()

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds_data = json.loads(settings.GMAIL_CREDENTIALS)
        creds = Credentials.from_authorized_user_info(creds_data)
        service = build("gmail", "v1", credentials=creds)

        results = (
            service.users()
            .messages()
            .list(userId="me", q="is:unread is:important", maxResults=10)
            .execute()
        )

        messages = results.get("messages", [])
        emails = []

        for msg in messages:
            detail = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )
            headers = {
                h["name"]: h["value"]
                for h in detail.get("payload", {}).get("headers", [])
            }
            emails.append({
                "subject": headers.get("Subject", "No Subject"),
                "from": headers.get("From", "Unknown"),
                "date": headers.get("Date", ""),
                "snippet": detail.get("snippet", "")[:150],
                "is_important": True,
            })

        return {
            "source": "gmail",
            "status": "success",
            "unread_count": len(emails),
            "emails": emails,
        }

    except ImportError:
        logger.info("Google API client not installed, using demo data")
        return _get_demo_emails()
    except Exception as e:
        logger.error(f"Gmail fetch error: {e}")
        return {
            "source": "gmail",
            "status": "error",
            "error": str(e),
            "emails": [],
        }


def _get_demo_emails() -> Dict[str, Any]:
    """Return demo email data for testing."""
    return {
        "source": "gmail",
        "status": "demo",
        "unread_count": 5,
        "emails": [
            {
                "subject": "Q3 Budget Approval Required",
                "from": "cfo@company.com",
                "date": datetime.now(timezone.utc).isoformat(),
                "snippet": "Please review and approve the Q3 budget allocation for the engineering team...",
                "is_important": True,
            },
            {
                "subject": "Production Alert: High CPU Usage",
                "from": "alerts@aws.amazon.com",
                "date": datetime.now(timezone.utc).isoformat(),
                "snippet": "Your EC2 instance i-0abc123 has exceeded 90% CPU utilization for 15 minutes...",
                "is_important": True,
            },
            {
                "subject": "PR Review Request: Auth Module Refactor",
                "from": "dev@company.com",
                "date": datetime.now(timezone.utc).isoformat(),
                "snippet": "I've completed the authentication module refactor. Could you review the changes?",
                "is_important": True,
            },
            {
                "subject": "Team Offsite Planning",
                "from": "hr@company.com",
                "date": datetime.now(timezone.utc).isoformat(),
                "snippet": "We're planning the annual team offsite for next month. Please fill out the survey...",
                "is_important": False,
            },
            {
                "subject": "AWS re:Invent Early Bird Registration",
                "from": "events@aws.amazon.com",
                "date": datetime.now(timezone.utc).isoformat(),
                "snippet": "Register now for AWS re:Invent 2026. Early bird pricing ends soon...",
                "is_important": False,
            },
        ],
    }

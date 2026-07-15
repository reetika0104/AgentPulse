"""
PULSE Notion Service
Fetches tasks and projects from Notion databases.
"""

import httpx
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("notion_service")
settings = get_settings()

NOTION_API_URL = "https://api.notion.com/v1"


async def fetch_notion_tasks() -> Dict[str, Any]:
    """
    Fetch tasks from Notion database.
    Returns structured task data for the AI agent.
    """
    try:
        if not settings.NOTION_API_KEY or not settings.NOTION_DATABASE_ID:
            logger.warning("Notion credentials not configured")
            return _get_demo_tasks()

        headers = {
            "Authorization": f"Bearer {settings.NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{NOTION_API_URL}/databases/{settings.NOTION_DATABASE_ID}/query",
                headers=headers,
                json={
                    "filter": {
                        "property": "Status",
                        "select": {"does_not_equal": "Done"},
                    },
                    "page_size": 10,
                },
            )

        if resp.status_code != 200:
            logger.error(f"Notion API error: {resp.status_code}")
            return _get_demo_tasks()

        results = resp.json().get("results", [])
        tasks = []
        for item in results:
            props = item.get("properties", {})
            title = ""
            if "Name" in props:
                title_items = props["Name"].get("title", [])
                title = title_items[0].get("plain_text", "") if title_items else ""

            tasks.append({
                "title": title,
                "status": props.get("Status", {}).get("select", {}).get("name", ""),
                "priority": props.get("Priority", {}).get("select", {}).get("name", ""),
                "due_date": props.get("Due", {}).get("date", {}).get("start", ""),
            })

        return {
            "source": "notion",
            "status": "success",
            "tasks_count": len(tasks),
            "tasks": tasks,
        }

    except Exception as e:
        logger.error(f"Notion fetch error: {e}")
        return {
            "source": "notion",
            "status": "error",
            "error": str(e),
            "tasks": [],
        }


def _get_demo_tasks() -> Dict[str, Any]:
    """Return demo Notion tasks."""
    return {
        "source": "notion",
        "status": "demo",
        "tasks_count": 6,
        "tasks": [
            {
                "title": "Finalize API documentation",
                "status": "In Progress",
                "priority": "High",
                "due_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            },
            {
                "title": "Review security audit findings",
                "status": "To Do",
                "priority": "Critical",
                "due_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            },
            {
                "title": "Prepare demo for stakeholders",
                "status": "In Progress",
                "priority": "High",
                "due_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            },
            {
                "title": "Update CI/CD pipeline",
                "status": "To Do",
                "priority": "Medium",
                "due_date": "",
            },
            {
                "title": "Implement caching layer",
                "status": "In Progress",
                "priority": "Medium",
                "due_date": "",
            },
            {
                "title": "Write unit tests for auth module",
                "status": "To Do",
                "priority": "Low",
                "due_date": "",
            },
        ],
    }

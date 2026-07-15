"""
PULSE GitHub Service
Fetches notifications, PRs, and repository activity.
"""

import httpx
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("github_service")
settings = get_settings()

GITHUB_API_BASE = "https://api.github.com"


async def fetch_github_notifications() -> Dict[str, Any]:
    """
    Fetch GitHub notifications and PR activity.
    Returns structured data for the AI agent.
    """
    try:
        if not settings.GITHUB_TOKEN:
            logger.warning("GitHub token not configured")
            return _get_demo_github()

        headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with httpx.AsyncClient() as client:
            # Fetch notifications
            notif_resp = await client.get(
                f"{GITHUB_API_BASE}/notifications",
                headers=headers,
                params={"all": "false", "per_page": 10},
            )
            notifications = notif_resp.json() if notif_resp.status_code == 200 else []

            # Fetch user's PRs that need review
            pr_resp = await client.get(
                f"{GITHUB_API_BASE}/search/issues",
                headers=headers,
                params={
                    "q": f"is:pr is:open review-requested:{settings.GITHUB_USERNAME}",
                    "per_page": 5,
                },
            )
            prs = pr_resp.json().get("items", []) if pr_resp.status_code == 200 else []

        return {
            "source": "github",
            "status": "success",
            "notifications_count": len(notifications),
            "notifications": [
                {
                    "repo": n.get("repository", {}).get("full_name", ""),
                    "type": n.get("subject", {}).get("type", ""),
                    "title": n.get("subject", {}).get("title", ""),
                    "reason": n.get("reason", ""),
                    "updated_at": n.get("updated_at", ""),
                }
                for n in notifications[:10]
            ],
            "pending_reviews": [
                {
                    "title": pr.get("title", ""),
                    "repo": pr.get("repository_url", "").split("/")[-1],
                    "author": pr.get("user", {}).get("login", ""),
                    "url": pr.get("html_url", ""),
                }
                for pr in prs
            ],
        }

    except Exception as e:
        logger.error(f"GitHub fetch error: {e}")
        return {
            "source": "github",
            "status": "error",
            "error": str(e),
            "notifications": [],
        }


def _get_demo_github() -> Dict[str, Any]:
    """Return demo GitHub data."""
    return {
        "source": "github",
        "status": "demo",
        "notifications_count": 6,
        "notifications": [
            {
                "repo": "company/api-service",
                "type": "PullRequest",
                "title": "feat: Add rate limiting middleware",
                "reason": "review_requested",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "repo": "company/infrastructure",
                "type": "Issue",
                "title": "Upgrade EKS cluster to 1.28",
                "reason": "assign",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "repo": "company/frontend",
                "type": "PullRequest",
                "title": "fix: Resolve dark mode flickering",
                "reason": "mention",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "repo": "company/data-pipeline",
                "type": "Issue",
                "title": "Data sync failing for EU region",
                "reason": "team_mention",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "repo": "company/mobile-app",
                "type": "PullRequest",
                "title": "chore: Update dependencies",
                "reason": "subscribed",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "repo": "opensource/cool-lib",
                "type": "Release",
                "title": "v3.0.0 - Breaking changes",
                "reason": "subscribed",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ],
        "pending_reviews": [
            {
                "title": "feat: Add rate limiting middleware",
                "repo": "api-service",
                "author": "colleague",
                "url": "https://github.com/company/api-service/pull/142",
            },
            {
                "title": "fix: Resolve dark mode flickering",
                "repo": "frontend",
                "author": "designer-dev",
                "url": "https://github.com/company/frontend/pull/89",
            },
        ],
    }

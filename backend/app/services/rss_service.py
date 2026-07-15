"""
PULSE RSS News Service
Fetches latest news from configured RSS feeds.
"""

import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("rss_service")
settings = get_settings()


async def fetch_news() -> Dict[str, Any]:
    """
    Fetch latest news from configured RSS feeds.
    Returns structured news data for the AI agent.
    """
    try:
        feeds = [f.strip() for f in settings.RSS_FEEDS.split(",") if f.strip()]

        if not feeds:
            return _get_demo_news()

        all_articles: List[Dict[str, str]] = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for feed_url in feeds:
                try:
                    resp = await client.get(feed_url)
                    if resp.status_code == 200:
                        articles = _parse_feed(resp.text, feed_url)
                        all_articles.extend(articles[:5])
                except Exception as e:
                    logger.warning(f"Failed to fetch feed {feed_url}: {e}")
                    continue

        if not all_articles:
            return _get_demo_news()

        return {
            "source": "rss",
            "status": "success",
            "articles_count": len(all_articles),
            "articles": all_articles[:10],
        }

    except Exception as e:
        logger.error(f"RSS fetch error: {e}")
        return _get_demo_news()


def _parse_feed(xml_content: str, feed_url: str) -> List[Dict[str, str]]:
    """Parse RSS/Atom feed XML into article list."""
    articles = []
    try:
        root = ET.fromstring(xml_content)

        # RSS 2.0
        for item in root.findall(".//item"):
            articles.append({
                "title": _get_text(item, "title"),
                "link": _get_text(item, "link"),
                "published": _get_text(item, "pubDate"),
                "source": feed_url.split("/")[2] if "/" in feed_url else feed_url,
            })

        # Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//atom:entry", ns):
            link_elem = entry.find("atom:link", ns)
            articles.append({
                "title": _get_text_ns(entry, "title", ns),
                "link": link_elem.get("href", "") if link_elem is not None else "",
                "published": _get_text_ns(entry, "published", ns) or _get_text_ns(entry, "updated", ns),
                "source": feed_url.split("/")[2] if "/" in feed_url else feed_url,
            })

    except ET.ParseError as e:
        logger.warning(f"Feed parse error: {e}")

    return articles


def _get_text(element, tag: str) -> str:
    """Safely get text content from XML element."""
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else ""


def _get_text_ns(element, tag: str, ns: dict) -> str:
    """Safely get text content from XML element with namespace."""
    child = element.find(f"atom:{tag}", ns)
    return child.text.strip() if child is not None and child.text else ""


def _get_demo_news() -> Dict[str, Any]:
    """Return demo news data."""
    return {
        "source": "rss",
        "status": "demo",
        "articles_count": 5,
        "articles": [
            {
                "title": "AWS Launches New Bedrock Features for Enterprise AI",
                "link": "https://aws.amazon.com/blogs/aws/new-bedrock-features",
                "published": datetime.now(timezone.utc).isoformat(),
                "source": "aws.amazon.com",
            },
            {
                "title": "Python 3.13 Released with Performance Improvements",
                "link": "https://python.org/downloads/release/python-313",
                "published": datetime.now(timezone.utc).isoformat(),
                "source": "python.org",
            },
            {
                "title": "Best Practices for Serverless Architecture in 2026",
                "link": "https://aws.amazon.com/blogs/compute/serverless-2026",
                "published": datetime.now(timezone.utc).isoformat(),
                "source": "aws.amazon.com",
            },
            {
                "title": "GitHub Copilot Workspace General Availability",
                "link": "https://github.blog/copilot-workspace-ga",
                "published": datetime.now(timezone.utc).isoformat(),
                "source": "github.blog",
            },
            {
                "title": "Understanding Amazon Nova: Multimodal AI Models",
                "link": "https://aws.amazon.com/blogs/ai/understanding-nova",
                "published": datetime.now(timezone.utc).isoformat(),
                "source": "aws.amazon.com",
            },
        ],
    }

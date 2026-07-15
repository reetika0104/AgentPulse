"""
PULSE Telegram Delivery
Sends morning brief via Telegram Bot.
"""

import httpx
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("telegram_delivery")
settings = get_settings()

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


async def send_telegram_brief(brief: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
    """
    Send morning brief via Telegram bot.
    
    Returns delivery status dict.
    """
    try:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            logger.warning("Telegram not configured, skipping")
            return {
                "channel": "telegram",
                "status": "skipped",
                "reason": "Telegram not configured",
            }

        message = _format_telegram_message(brief)
        url = f"{TELEGRAM_API_BASE}{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json={
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
            )

        if resp.status_code == 200:
            result = resp.json()
            message_id = result.get("result", {}).get("message_id", "")
            logger.info(f"Telegram message sent: {message_id}")
            return {
                "channel": "telegram",
                "status": "delivered",
                "message_id": str(message_id),
                "delivered_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            error = resp.text
            logger.error(f"Telegram API error: {error}")
            return {
                "channel": "telegram",
                "status": "failed",
                "error_message": error,
            }

    except Exception as e:
        logger.error(f"Telegram delivery error: {e}")
        return {
            "channel": "telegram",
            "status": "failed",
            "error_message": str(e),
        }


def _format_telegram_message(brief: Dict[str, Any]) -> str:
    """Format brief as Telegram message with markdown."""
    priority = brief.get("priority_score", 5)
    emoji = "🔴" if priority >= 8 else "🟡" if priority >= 5 else "🟢"

    urgent_items = brief.get("urgent_items", [])
    urgent_section = ""
    if urgent_items:
        urgent_list = "\n".join(
            f"  ⚠️ {item.get('item', '')} ({item.get('source', '')})"
            for item in urgent_items[:5]
        )
        urgent_section = f"\n\n🚨 *Urgent Items:*\n{urgent_list}"

    meetings = brief.get("meetings", {})
    meeting_notes = "\n".join(
        f"  • {note}" for note in meetings.get("preparation_notes", [])[:5]
    )

    tips = "\n".join(
        f"  💡 {tip}" for tip in brief.get("productivity_tips", [])[:3]
    )

    return f"""⚡ *PULSE Morning Brief*
{datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

{brief.get('greeting', 'Good morning!')}

{emoji} *Priority: {priority}/10*
🎯 *Focus:* {brief.get('suggested_focus', '')}

{brief.get('executive_summary', '')}
{urgent_section}

📅 *Meetings ({meetings.get('count', 0)}):*
{meeting_notes}

🌤️ *Weather:* {brief.get('weather', {}).get('summary', 'N/A')}

*Productivity Tips:*
{tips}

_{brief.get('closing_note', 'Have a great day!')}_
"""

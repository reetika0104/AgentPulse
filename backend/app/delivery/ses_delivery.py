"""
PULSE Amazon SES Delivery
Sends formatted morning brief via email using Amazon SES.
"""

import boto3
from datetime import datetime, timezone
from typing import Dict, Any
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("ses_delivery")
settings = get_settings()


def get_ses_client():
    """Get boto3 SES client."""
    return boto3.client("ses", region_name=settings.AWS_REGION)


async def send_email_brief(brief: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
    """
    Send morning brief via Amazon SES.
    
    Returns delivery status dict.
    """
    try:
        if not settings.SES_SENDER_EMAIL or not settings.SES_RECIPIENT_EMAIL:
            logger.warning("SES not configured, skipping email delivery")
            return {
                "channel": "email",
                "status": "skipped",
                "reason": "SES not configured",
            }

        html_body = _format_brief_html(brief)
        text_body = _format_brief_text(brief)

        client = get_ses_client()
        response = client.send_email(
            Source=f"PULSE Agent <{settings.SES_SENDER_EMAIL}>",
            Destination={"ToAddresses": [settings.SES_RECIPIENT_EMAIL]},
            Message={
                "Subject": {
                    "Data": f"☀️ PULSE Morning Brief - {datetime.now(timezone.utc).strftime('%A, %b %d')}",
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                },
            },
        )

        message_id = response.get("MessageId", "")
        logger.info(f"Email sent successfully: {message_id}")

        return {
            "channel": "email",
            "status": "delivered",
            "message_id": message_id,
            "recipient": settings.SES_RECIPIENT_EMAIL,
            "delivered_at": datetime.now(timezone.utc).isoformat(),
        }

    except ClientError as e:
        error_msg = e.response["Error"]["Message"]
        logger.error(f"SES delivery error: {error_msg}")
        return {
            "channel": "email",
            "status": "failed",
            "error_message": error_msg,
        }
    except Exception as e:
        logger.error(f"Email delivery error: {e}")
        return {
            "channel": "email",
            "status": "failed",
            "error_message": str(e),
        }


def _format_brief_html(brief: Dict[str, Any]) -> str:
    """Format the brief as professional HTML email."""
    priority = brief.get("priority_score", 5)
    priority_color = "#ef4444" if priority >= 8 else "#f59e0b" if priority >= 5 else "#10b981"

    meetings = brief.get("meetings", {})
    urgent = brief.get("urgent_items", [])
    weather = brief.get("weather", {})
    tips = brief.get("productivity_tips", [])

    urgent_html = ""
    if urgent:
        urgent_items = "".join(
            f'<li style="margin-bottom:8px;"><strong>{item.get("item", "")}</strong> '
            f'<span style="color:#6b7280;">({item.get("source", "")})</span><br/>'
            f'<em>{item.get("action", "")}</em></li>'
            for item in urgent
        )
        urgent_html = f"""
        <div style="background:#fef2f2;border-left:4px solid #ef4444;padding:16px;margin:16px 0;border-radius:4px;">
            <h3 style="color:#dc2626;margin-top:0;">🚨 Urgent Items</h3>
            <ul style="margin:0;padding-left:20px;">{urgent_items}</ul>
        </div>"""

    tips_html = "".join(f"<li>{tip}</li>" for tip in tips)

    return f"""
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#f9fafb;">
        <div style="background:#1e293b;color:white;padding:32px;border-radius:12px;margin-bottom:20px;">
            <h1 style="margin:0;font-size:24px;">PULSE</h1>
            <p style="margin:8px 0 0;opacity:0.8;font-size:14px;">Your AI Digital Chief of Staff</p>
            <p style="margin:16px 0 0;font-size:18px;">{brief.get('greeting', 'Good morning!')}</p>
        </div>
        
        <div style="background:white;padding:24px;border-radius:12px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <table cellpadding="0" cellspacing="0" border="0" style="width:100%;">
                <tr>
                    <td style="width:56px;vertical-align:top;padding-right:16px;">
                        <div style="background:{priority_color};color:white;width:48px;height:48px;border-radius:50%;text-align:center;line-height:48px;font-weight:bold;font-size:20px;">
                            {priority}
                        </div>
                    </td>
                    <td style="vertical-align:top;">
                        <p style="margin:0;font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Priority Score</p>
                        <p style="margin:4px 0 0;font-weight:600;font-size:15px;color:#1f2937;">{brief.get('suggested_focus', '')}</p>
                    </td>
                </tr>
            </table>
            <p style="color:#374151;line-height:1.6;margin-top:16px;">{brief.get('executive_summary', '')}</p>
        </div>

        {urgent_html}
        
        <div style="background:white;padding:24px;border-radius:12px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0;color:#1f2937;">Meetings ({meetings.get('count', 0)})</h3>
            <ul style="color:#374151;">{"".join(f"<li>{n}</li>" for n in meetings.get('preparation_notes', []))}</ul>
        </div>

        <div style="background:white;padding:24px;border-radius:12px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0;color:#1f2937;">Weather</h3>
            <p style="color:#374151;">{weather.get('summary', 'N/A')}</p>
            <p style="color:#6b7280;font-style:italic;">{weather.get('outfit_suggestion', '')}</p>
        </div>

        <div style="background:white;padding:24px;border-radius:12px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0;color:#1f2937;">Productivity Tips</h3>
            <ul style="color:#374151;">{tips_html}</ul>
        </div>

        <div style="background:#f0fdf4;padding:16px;border-radius:8px;text-align:center;margin-top:20px;">
            <p style="margin:0;color:#166534;font-style:italic;">{brief.get('closing_note', 'Have a great day!')}</p>
        </div>
        
        <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:24px;">
            Generated by PULSE • Powered by Amazon Bedrock
        </p>
    </body>
    </html>
    """


def _format_brief_text(brief: Dict[str, Any]) -> str:
    """Format the brief as plain text."""
    lines = [
        "⚡ PULSE - Morning Brief",
        "=" * 40,
        "",
        brief.get("greeting", "Good morning!"),
        "",
        f"Priority Score: {brief.get('priority_score', 'N/A')}/10",
        f"Focus: {brief.get('suggested_focus', '')}",
        "",
        brief.get("executive_summary", ""),
        "",
        f"📅 Meetings: {brief.get('meetings', {}).get('count', 0)}",
        f"📧 Unread Important: {brief.get('emails', {}).get('unread_important', 0)}",
        f"🐙 GitHub: {brief.get('github', {}).get('notifications', 0)} notifications",
        "",
        "💡 Tips:",
    ]
    for tip in brief.get("productivity_tips", []):
        lines.append(f"  • {tip}")
    lines.extend(["", brief.get("closing_note", "Have a great day!")])
    return "\n".join(lines)

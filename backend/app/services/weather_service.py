"""
PULSE Weather Service
Fetches current weather and forecast data.
"""

import httpx
from typing import Dict, Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("weather_service")
settings = get_settings()

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


async def fetch_weather() -> Dict[str, Any]:
    """
    Fetch weather data for the configured city.
    Returns structured weather data for the AI agent.
    """
    try:
        if not settings.WEATHER_API_KEY:
            logger.warning("Weather API key not configured")
            return _get_demo_weather()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                WEATHER_API_URL,
                params={
                    "q": settings.WEATHER_CITY,
                    "appid": settings.WEATHER_API_KEY,
                    "units": "metric",
                },
            )

        if resp.status_code != 200:
            logger.error(f"Weather API error: {resp.status_code}")
            return _get_demo_weather()

        data = resp.json()
        return {
            "source": "weather",
            "status": "success",
            "city": data.get("name", settings.WEATHER_CITY),
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed_ms": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"],
        }

    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return {
            "source": "weather",
            "status": "error",
            "error": str(e),
        }


def _get_demo_weather() -> Dict[str, Any]:
    """Return demo weather data."""
    return {
        "source": "weather",
        "status": "demo",
        "city": settings.WEATHER_CITY,
        "temperature_c": 22,
        "feels_like_c": 24,
        "humidity": 55,
        "description": "partly cloudy",
        "wind_speed_ms": 3.2,
        "icon": "02d",
    }

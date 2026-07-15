"""
PULSE Structured Logging Module
Production-grade logging with JSON formatting and CloudWatch compatibility.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for CloudWatch and structured log analysis."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        return json.dumps(log_entry, default=str)


class PulseLogger:
    """Custom logger with structured logging support."""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        extra = {"extra_data": kwargs} if kwargs else {}
        self.logger.log(level, message, extra=extra)


def get_logger(name: str = "pulse") -> PulseLogger:
    """Get a configured logger instance."""
    from app.core.config import get_settings
    settings = get_settings()
    return PulseLogger(name, settings.LOG_LEVEL)

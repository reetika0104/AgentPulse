"""
PULSE Database Module
SQLite with easy migration path to DynamoDB.
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("database")

DATABASE_PATH = settings.DATABASE_URL.replace("sqlite:///", "")


def init_database() -> None:
    """Initialize the database schema."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                trigger_source TEXT NOT NULL DEFAULT 'scheduler',
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds REAL,
                sources_collected TEXT,
                brief_content TEXT,
                delivery_status TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS briefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                brief_date TEXT NOT NULL,
                content TEXT NOT NULL,
                priority_score REAL,
                urgent_items INTEGER DEFAULT 0,
                meetings_today INTEGER DEFAULT 0,
                ai_model TEXT,
                tokens_used INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
            );

            CREATE TABLE IF NOT EXISTS delivery_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT NOT NULL,
                recipient TEXT,
                message_id TEXT,
                error_message TEXT,
                delivered_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
            );

            CREATE TABLE IF NOT EXISTS agent_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_time TEXT NOT NULL,
                service_name TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time_ms REAL,
                details TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
            CREATE INDEX IF NOT EXISTS idx_executions_started ON executions(started_at);
            CREATE INDEX IF NOT EXISTS idx_briefs_date ON briefs(brief_date);
        """)
        logger.info("Database initialized successfully")


@contextmanager
def get_connection():
    """Get a database connection context manager."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def save_execution(execution_data: Dict[str, Any]) -> None:
    """Save an execution record."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO executions 
               (execution_id, status, trigger_source, started_at, sources_collected)
               VALUES (?, ?, ?, ?, ?)""",
            (
                execution_data["execution_id"],
                execution_data.get("status", "running"),
                execution_data.get("trigger_source", "scheduler"),
                execution_data.get("started_at", datetime.now(timezone.utc).isoformat()),
                json.dumps(execution_data.get("sources_collected", [])),
            ),
        )


def update_execution(execution_id: str, updates: Dict[str, Any]) -> None:
    """Update an execution record."""
    with get_connection() as conn:
        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(json.dumps(value) if isinstance(value, (dict, list)) else value)
        values.append(execution_id)
        conn.execute(
            f"UPDATE executions SET {', '.join(set_clauses)} WHERE execution_id = ?",
            values,
        )


def save_brief(brief_data: Dict[str, Any]) -> None:
    """Save a generated brief."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO briefs 
               (execution_id, brief_date, content, priority_score, 
                urgent_items, meetings_today, ai_model, tokens_used)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                brief_data["execution_id"],
                brief_data["brief_date"],
                brief_data["content"],
                brief_data.get("priority_score", 0),
                brief_data.get("urgent_items", 0),
                brief_data.get("meetings_today", 0),
                brief_data.get("ai_model", "amazon.nova-micro-v1:0"),
                brief_data.get("tokens_used", 0),
            ),
        )


def get_latest_brief() -> Optional[Dict[str, Any]]:
    """Get the most recent brief."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM briefs ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_executions(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent execution records."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM executions ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific execution record."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM executions WHERE execution_id = ?",
            (execution_id,),
        ).fetchone()
        return dict(row) if row else None


def save_delivery_log(log_data: Dict[str, Any]) -> None:
    """Save a delivery log entry."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO delivery_logs 
               (execution_id, channel, status, recipient, message_id, error_message, delivered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                log_data["execution_id"],
                log_data["channel"],
                log_data["status"],
                log_data.get("recipient"),
                log_data.get("message_id"),
                log_data.get("error_message"),
                log_data.get("delivered_at"),
            ),
        )


def save_health_check(health_data: Dict[str, Any]) -> None:
    """Save a health check result."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO agent_health 
               (check_time, service_name, status, response_time_ms, details)
               VALUES (?, ?, ?, ?, ?)""",
            (
                health_data["check_time"],
                health_data["service_name"],
                health_data["status"],
                health_data.get("response_time_ms"),
                health_data.get("details"),
            ),
        )


def get_health_status() -> List[Dict[str, Any]]:
    """Get the latest health status for each service."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM agent_health 
               WHERE id IN (
                   SELECT MAX(id) FROM agent_health GROUP BY service_name
               )
               ORDER BY service_name"""
        ).fetchall()
        return [dict(row) for row in rows]

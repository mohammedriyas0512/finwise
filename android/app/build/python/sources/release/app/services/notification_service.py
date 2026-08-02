"""
Service for creating notifications and writing activity audit logs.

Both are thin wrappers around the ORM so routers don't need to know the schema
shape, keeping a clean separation between API layer and persistence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import ActivityLog, Notification


def log_activity(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    entity: Optional[str] = None,
    entity_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> ActivityLog:
    """Persist an audit-log entry."""
    import json

    entry = ActivityLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip_address,
        meta=json.dumps(metadata or {}, default=str),
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def create_notification(
    db: Session,
    *,
    user_id: int,
    title: str,
    message: str,
    ntype: str = "info",
) -> Notification:
    """Create and persist a notification for a user."""
    note = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=ntype,
        is_read=False,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

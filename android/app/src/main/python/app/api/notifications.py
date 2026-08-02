"""
Notification endpoints: list, mark read, delete.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Notification
from app.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(db: DbSession, current_user: CurrentUser, unread_only: bool = False, limit: int = 50):
    stmt = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(notification_id: int, db: DbSession, current_user: CurrentUser):
    note = db.get(Notification, notification_id)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    note.is_read = True
    db.commit()
    db.refresh(note)
    return note


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(db: DbSession, current_user: CurrentUser):
    db.execute(
        Notification.__table__.update()
        .where(Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    db.commit()
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(notification_id: int, db: DbSession, current_user: CurrentUser):
    note = db.get(Notification, notification_id)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    db.delete(note)
    db.commit()
    return {"message": "Notification deleted"}

"""
Dashboard endpoints: KPI summary, charts, health score, upcoming items.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.services.analytics_service import dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary(db: DbSession, current_user: CurrentUser):
    return dashboard_summary(db, current_user.id)

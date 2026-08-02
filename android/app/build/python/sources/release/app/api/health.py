"""
Financial Health score endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.services.analytics_service import dashboard_summary

router = APIRouter(prefix="/health", tags=["Financial Health"])


@router.get("")
def health_score(db: DbSession, current_user: CurrentUser):
    summary = dashboard_summary(db, current_user.id)
    return summary["financial_health"]

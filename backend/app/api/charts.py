"""
Charts endpoints: pie/bar/line data for frontend visualisations.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.services.analytics_service import (
    expense_chart,
    income_chart,
    monthly_analysis,
    savings_trend,
)

router = APIRouter(prefix="/charts", tags=["Charts"])


@router.get("/expense-breakdown")
def expense_breakdown(db: DbSession, current_user: CurrentUser):
    return expense_chart(db, current_user.id)


@router.get("/income-breakdown")
def income_breakdown(db: DbSession, current_user: CurrentUser):
    return income_chart(db, current_user.id)


@router.get("/monthly-analysis")
def monthly(db: DbSession, current_user: CurrentUser, months: int = Query(6, ge=1, le=24)):
    return monthly_analysis(db, current_user.id, months)


@router.get("/savings-trend")
def savings(db: DbSession, current_user: CurrentUser, months: int = Query(6, ge=1, le=24)):
    return savings_trend(db, current_user.id, months)


@router.get("/category-analysis")
def category_analysis(db: DbSession, current_user: CurrentUser, txn_type: str = Query("expense", pattern="^(income|expense)$")):
    if txn_type == "income":
        return income_chart(db, current_user.id)
    return expense_chart(db, current_user.id)

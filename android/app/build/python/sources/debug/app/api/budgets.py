"""
Budget planner endpoints: per-category monthly budgets with spend tracking.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Budget
from app.schemas import BudgetCreate, BudgetResponse, BudgetUpdate
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip, money

router = APIRouter(prefix="/budgets", tags=["Budget"])


@router.get("", response_model=list[BudgetResponse])
def list_budgets(db: DbSession, current_user: CurrentUser, month: str | None = None):
    stmt = select(Budget).where(Budget.user_id == current_user.id)
    if month:
        stmt = stmt.where(Budget.month == month)
    stmt = stmt.order_by(Budget.month.desc(), Budget.category)
    rows = db.scalars(stmt).all()
    return [_serialize(b) for b in rows]


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, request: Request, db: DbSession, current_user: CurrentUser):
    existing = db.scalar(select(Budget).where(
        Budget.user_id == current_user.id,
        Budget.month == payload.month,
        Budget.category == payload.category,
    ))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget for this category/month already exists. Use PATCH to update.",
        )
    budget = Budget(user_id=current_user.id, spent_amount=0, **payload.dict())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    log_activity(db, user_id=current_user.id, action="create_budget", entity="budget",
                entity_id=budget.id, ip_address=client_ip(request))
    return _serialize(budget)


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, payload: BudgetUpdate, request: Request, db: DbSession, current_user: CurrentUser):
    budget = db.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    if payload.limit_amount is not None:
        budget.limit_amount = payload.limit_amount
    db.commit()
    db.refresh(budget)
    log_activity(db, user_id=current_user.id, action="update_budget", entity="budget",
                entity_id=budget.id, ip_address=client_ip(request))
    return _serialize(budget)


@router.delete("/{budget_id}", status_code=status.HTTP_200_OK)
def delete_budget(budget_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    budget = db.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    db.delete(budget)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_budget", entity="budget",
                entity_id=budget_id, ip_address=client_ip(request))
    return {"message": "Budget deleted successfully"}


def _serialize(b: Budget) -> dict:
    spent = float(b.spent_amount)
    limit = float(b.limit_amount)
    remaining = max(0.0, limit - spent)
    usage = round((spent / limit) * 100, 1) if limit > 0 else 0.0
    return {
        "id": b.id,
        "user_id": b.user_id,
        "month": b.month,
        "category": b.category,
        "limit_amount": limit,
        "spent_amount": spent,
        "remaining": remaining,
        "usage_percent": usage,
        "created_at": b.created_at,
        "updated_at": b.updated_at,
    }

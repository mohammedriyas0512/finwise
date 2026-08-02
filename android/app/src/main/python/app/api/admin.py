"""
Admin panel endpoints: user management, system statistics, activity logs.
Guarded by RBAC (require_admin).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.deps import AdminUser, CurrentUser, DbSession
from app.models import ActivityLog, Expense, Income, User
from app.schemas import AdminUserResponse, ActivityLogResponse
from app.utils.helpers import client_ip

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def system_stats(db: DbSession, _: AdminUser):
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_income = float(db.scalar(select(func.coalesce(func.sum(Income.amount), 0))) or 0)
    total_expense = float(db.scalar(select(func.coalesce(func.sum(Expense.amount), 0))) or 0)
    avg_savings = (total_income - total_expense) / total_users if total_users else 0

    # Most used expense category.
    top_cat_row = db.execute(
        select(Expense.category, func.count().label("cnt"))
        .group_by(Expense.category).order_by(func.count().desc()).limit(1)
    ).first()

    now = datetime.now(timezone.utc)
    new_users_30d = db.scalar(
        select(func.count()).select_from(User).where(User.created_at >= now - timedelta(days=30))
    ) or 0

    return {
        "total_users": total_users,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "average_savings": round(avg_savings, 2),
        "most_used_category": top_cat_row[0] if top_cat_row else None,
        "new_users_last_30d": new_users_30d,
    }


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(db: DbSession, _: AdminUser, skip: int = 0, limit: int = 100, search: str | None = None):
    stmt = select(User).order_by(User.created_at.desc())
    if search:
        stmt = stmt.where(User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%"))
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.patch("/users/{user_id}/toggle-active", response_model=AdminUserResponse)
def toggle_active(user_id: int, db: DbSession, admin: AdminUser):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: DbSession, admin: AdminUser):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == "admin":
        remaining = db.scalar(select(User).where(User.role == "admin", User.id != user.id))
        if not remaining:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the last admin")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/activity", response_model=list[ActivityLogResponse])
def activity_logs(db: DbSession, _: AdminUser, limit: int = Query(100, ge=1, le=500), skip: int = 0):
    return db.scalars(
        select(ActivityLog).order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
    ).all()

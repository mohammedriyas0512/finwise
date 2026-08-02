"""
Savings goals endpoints with auto-computed progress.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import SavingGoal
from app.schemas import GoalCreate, GoalResponse, GoalUpdate
from app.services.notification_service import create_notification, log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/goals", tags=["Savings Goals"])


@router.get("", response_model=list[GoalResponse])
def list_goals(db: DbSession, current_user: CurrentUser):
    return db.scalars(
        select(SavingGoal).where(SavingGoal.user_id == current_user.id).order_by(SavingGoal.deadline.asc())
    ).all()


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, request: Request, db: DbSession, current_user: CurrentUser):
    if payload.current_amount > payload.target_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Current amount cannot exceed target amount",
        )
    goal = SavingGoal(user_id=current_user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    log_activity(db, user_id=current_user.id, action="create_goal", entity="goal",
                entity_id=goal.id, ip_address=client_ip(request))
    return _serialize(goal)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: int, db: DbSession, current_user: CurrentUser):
    goal = db.get(SavingGoal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return _serialize(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, payload: GoalUpdate, request: Request, db: DbSession, current_user: CurrentUser):
    goal = db.get(SavingGoal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    if goal.current_amount >= goal.target_amount:
        create_notification(db, user_id=current_user.id, title="Goal achieved",
                            message=f"🏆 You reached your '{goal.name}' savings goal!", ntype="goal")
    db.commit()
    db.refresh(goal)
    log_activity(db, user_id=current_user.id, action="update_goal", entity="goal",
                entity_id=goal.id, ip_address=client_ip(request))
    return _serialize(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_200_OK)
def delete_goal(goal_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    goal = db.get(SavingGoal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    db.delete(goal)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_goal", entity="goal",
                entity_id=goal_id, ip_address=client_ip(request))
    return {"message": "Goal deleted successfully"}


def _serialize(g: SavingGoal) -> dict:
    target = float(g.target_amount)
    current = float(g.current_amount)
    progress = round((current / target) * 100, 1) if target > 0 else 0.0
    return {
        "id": g.id,
        "user_id": g.user_id,
        "name": g.name,
        "target_amount": target,
        "current_amount": current,
        "deadline": g.deadline,
        "progress_percent": progress,
        "remaining_amount": max(0.0, target - current),
        "created_at": g.created_at,
        "updated_at": g.updated_at,
    }

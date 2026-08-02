"""
Income management endpoints: CRUD + search/filter/sort.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Income, Transaction
from app.schemas import IncomeCreate, IncomeResponse, IncomeUpdate
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip, money

router = APIRouter(prefix="/income", tags=["Income"])


@router.get("", response_model=list[IncomeResponse])
def list_income(
    db: DbSession,
    current_user: CurrentUser,
    category: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("date", pattern="^(date|amount|category)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    stmt = select(Income).where(Income.user_id == current_user.id)
    if category:
        stmt = stmt.where(Income.category == category)
    if search:
        stmt = stmt.where(Income.description.ilike(f"%{search}%"))
    column = getattr(Income, sort_by)
    stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeCreate, request: Request, db: DbSession, current_user: CurrentUser):
    income = Income(user_id=current_user.id, **payload.model_dump())
    db.add(income)
    db.flush()

    # Mirror into unified transactions table for fast global search.
    db.add(Transaction(
        user_id=current_user.id,
        txn_type="income",
        amount=payload.amount,
        category=payload.category,
        description=payload.description,
        date=payload.date,
        reference_id=income.id,
    ))
    db.commit()
    db.refresh(income)
    log_activity(db, user_id=current_user.id, action="create_income", entity="income",
                entity_id=income.id, ip_address=client_ip(request))
    return income


@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(income_id: int, db: DbSession, current_user: CurrentUser):
    income = db.get(Income, income_id)
    if not income or income.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income not found")
    return income


@router.patch("/{income_id}", response_model=IncomeResponse)
def update_income(income_id: int, payload: IncomeUpdate, request: Request, db: DbSession, current_user: CurrentUser):
    income = db.get(Income, income_id)
    if not income or income.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(income, field, value)
    # keep the mirrored transaction in sync
    txn = db.scalar(select(Transaction).where(
        Transaction.user_id == current_user.id,
        Transaction.txn_type == "income",
        Transaction.reference_id == income.id,
    ))
    if txn:
        txn.amount = income.amount
        txn.category = income.category
        txn.description = income.description
        txn.date = income.date
    db.commit()
    db.refresh(income)
    log_activity(db, user_id=current_user.id, action="update_income", entity="income",
                entity_id=income.id, ip_address=client_ip(request))
    return income


@router.delete("/{income_id}", status_code=status.HTTP_200_OK)
def delete_income(income_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    income = db.get(Income, income_id)
    if not income or income.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income not found")
    db.execute(
        Transaction.__table__.delete().where(
            Transaction.user_id == current_user.id,
            Transaction.txn_type == "income",
            Transaction.reference_id == income.id,
        )
    )
    db.delete(income)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_income", entity="income",
                entity_id=income_id, ip_address=client_ip(request))
    return {"message": "Income deleted successfully"}

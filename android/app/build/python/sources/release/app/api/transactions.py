"""
Global transaction search + filters (date, category, amount, type).
Reads from the unified ``transactions`` mirror table for fast queries.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Transaction
from app.schemas import TransactionResponse
from app.utils.helpers import money

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=list[TransactionResponse])
def search_transactions(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = Query(None, description="Free text search"),
    txn_type: str | None = Query(None, regex="^(income|expense)$"),
    category: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    min_amount: float | None = Query(None, ge=0),
    max_amount: float | None = Query(None, ge=0),
    sort_by: str = Query("date", regex="^(date|amount)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    stmt = select(Transaction).where(Transaction.user_id == current_user.id)
    if q:
        stmt = stmt.where(Transaction.description.ilike(f"%{q}%"))
    if txn_type:
        stmt = stmt.where(Transaction.txn_type == txn_type)
    if category:
        stmt = stmt.where(Transaction.category == category)
    if date_from:
        stmt = stmt.where(Transaction.date >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.date <= date_to)
    if min_amount is not None:
        stmt = stmt.where(Transaction.amount >= min_amount)
    if max_amount is not None:
        stmt = stmt.where(Transaction.amount <= max_amount)
    column = getattr(Transaction, sort_by)
    stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()

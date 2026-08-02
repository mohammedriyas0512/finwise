"""
Expense management endpoints: CRUD + search/filter/sort.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Budget, Expense, Transaction
from app.schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.services.notification_service import create_notification, log_activity
from app.utils.helpers import client_ip, money, month_key

router = APIRouter(prefix="/expenses", tags=["Expense"])


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    db: DbSession,
    current_user: CurrentUser,
    category: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("date", regex="^(date|amount|category)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    stmt = select(Expense).where(Expense.user_id == current_user.id)
    if category:
        stmt = stmt.where(Expense.category == category)
    if search:
        stmt = stmt.where(Expense.description.ilike(f"%{search}%"))
    column = getattr(Expense, sort_by)
    stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, request: Request, db: DbSession, current_user: CurrentUser):
    expense = Expense(user_id=current_user.id, **payload.dict())
    db.add(expense)
    db.flush()

    db.add(Transaction(
        user_id=current_user.id,
        txn_type="expense",
        amount=payload.amount,
        category=payload.category,
        description=payload.description,
        date=payload.date,
        reference_id=expense.id,
    ))

    # Bump the matching monthly budget spend and raise an alert if needed.
    _update_budget(db, current_user.id, payload.category, month_key(payload.date), float(payload.amount))
    db.commit()
    db.refresh(expense)
    log_activity(db, user_id=current_user.id, action="create_expense", entity="expense",
                entity_id=expense.id, ip_address=client_ip(request))
    return expense


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: DbSession, current_user: CurrentUser):
    expense = db.get(Expense, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, payload: ExpenseUpdate, request: Request, db: DbSession, current_user: CurrentUser):
    expense = db.get(Expense, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    old_amount = float(expense.amount)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(expense, field, value)
    txn = db.scalar(select(Transaction).where(
        Transaction.user_id == current_user.id,
        Transaction.txn_type == "expense",
        Transaction.reference_id == expense.id,
    ))
    if txn:
        txn.amount = expense.amount
        txn.category = expense.category
        txn.description = expense.description
        txn.date = expense.date
    # Reconcile budget spend if amount/category/month changed.
    if float(expense.amount) != old_amount or payload.category is not None:
        _reconcile_budget(db, current_user.id, expense)
    db.commit()
    db.refresh(expense)
    log_activity(db, user_id=current_user.id, action="update_expense", entity="expense",
                entity_id=expense.id, ip_address=client_ip(request))
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_200_OK)
def delete_expense(expense_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    expense = db.get(Expense, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    # Revert budget spend for this expense.
    budget = db.scalar(select(Budget).where(
        Budget.user_id == current_user.id,
        Budget.month == month_key(expense.date),
        Budget.category == expense.category,
    ))
    if budget:
        budget.spent_amount = max(0.0, float(budget.spent_amount) - float(expense.amount))

    db.execute(
        Transaction.__table__.delete().where(
            Transaction.user_id == current_user.id,
            Transaction.txn_type == "expense",
            Transaction.reference_id == expense.id,
        )
    )
    db.delete(expense)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_expense", entity="expense",
                entity_id=expense_id, ip_address=client_ip(request))
    return {"message": "Expense deleted successfully"}


def _update_budget(db: Session, user_id: int, category: str, month: str, amount: float) -> None:
    budget = db.scalar(select(Budget).where(
        Budget.user_id == user_id, Budget.month == month, Budget.category == category
    ))
    if not budget:
        return
    budget.spent_amount = float(budget.spent_amount) + amount
    if float(budget.spent_amount) > float(budget.limit_amount):
        create_notification(
            db, user_id=user_id,
            title="Budget exceeded",
            message=f"You exceeded your {category} budget for {month}.",
            ntype="budget",
        )


def _reconcile_budget(db: Session, user_id: int, expense: Expense) -> None:
    # Simple recompute: reset spent to sum of expenses in that month/category.
    total = db.scalar(
        select(__import__("sqlalchemy").func.sum(Expense.amount)).where(
            Expense.user_id == user_id,
            Expense.category == expense.category,
        )
    )
    budget = db.scalar(select(Budget).where(
        Budget.user_id == user_id,
        Budget.month == month_key(expense.date),
        Budget.category == expense.category,
    ))
    if budget:
        budget.spent_amount = float(total or 0.0)

"""
Debt tracker endpoints: credit card, personal loan, borrowed money, etc.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Debt, DebtPayment
from app.schemas import (
    DebtCreate,
    DebtPaymentCreate,
    DebtPaymentResponse,
    DebtResponse,
    DebtUpdate,
    DebtWithPayments,
)
from app.services.notification_service import create_notification, log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/debts", tags=["Debt"])


@router.get("", response_model=list[DebtResponse])
def list_debts(db: DbSession, current_user: CurrentUser):
    return db.scalars(
        select(Debt).where(Debt.user_id == current_user.id).order_by(Debt.due_date.asc())
    ).all()


@router.post("", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
def create_debt(payload: DebtCreate, request: Request, db: DbSession, current_user: CurrentUser):
    if payload.remaining_balance > payload.total_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Remaining balance cannot exceed total amount",
        )
    debt = Debt(user_id=current_user.id, **payload.model_dump())
    db.add(debt)
    db.commit()
    db.refresh(debt)
    log_activity(db, user_id=current_user.id, action="create_debt", entity="debt",
                entity_id=debt.id, ip_address=client_ip(request))
    return debt


@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(debt_id: int, db: DbSession, current_user: CurrentUser):
    debt = db.get(Debt, debt_id)
    if not debt or debt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    return debt


@router.patch("/{debt_id}", response_model=DebtResponse)
def update_debt(debt_id: int, payload: DebtUpdate, request: Request, db: DbSession, current_user: CurrentUser):
    debt = db.get(Debt, debt_id)
    if not debt or debt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(debt, field, value)
    if debt.remaining_balance <= 0:
        debt.status = "paid"
        create_notification(db, user_id=current_user.id, title="Debt cleared",
                            message=f"🎉 {debt.name} is fully paid off!", ntype="debt")
    db.commit()
    db.refresh(debt)
    log_activity(db, user_id=current_user.id, action="update_debt", entity="debt",
                entity_id=debt.id, ip_address=client_ip(request))
    return debt


@router.delete("/{debt_id}", status_code=status.HTTP_200_OK)
def delete_debt(debt_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    debt = db.get(Debt, debt_id)
    if not debt or debt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    db.delete(debt)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_debt", entity="debt",
                entity_id=debt_id, ip_address=client_ip(request))
    return {"message": "Debt deleted successfully"}


# --- Repayments -------------------------------------------------------------
def _owned_debt(debt_id: int, db: Session, user_id: int) -> Debt:
    debt = db.get(Debt, debt_id)
    if not debt or debt.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    return debt


@router.get("/{debt_id}/payments", response_model=DebtWithPayments)
def list_payments(debt_id: int, db: DbSession, current_user: CurrentUser):
    """Return a debt together with its repayment history and total paid so far."""
    debt = _owned_debt(debt_id, db, current_user.id)
    total_paid = sum(float(p.amount) for p in debt.payments)
    return DebtWithPayments(
        **DebtResponse.model_validate(debt).model_dump(),
        total_paid=total_paid,
        payments=debt.payments,
    )


@router.post("/{debt_id}/payments", response_model=DebtWithPayments, status_code=status.HTTP_201_CREATED)
def add_payment(debt_id: int, payload: DebtPaymentCreate, request: Request, db: DbSession, current_user: CurrentUser):
    """Record a repayment, decrement the remaining balance, and mark paid when cleared."""
    debt = _owned_debt(debt_id, db, current_user.id)
    if payload.amount > float(debt.remaining_balance):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment cannot exceed the remaining balance",
        )
    payment = DebtPayment(
        debt_id=debt.id,
        user_id=current_user.id,
        amount=payload.amount,
        note=payload.note,
        **({"paid_at": payload.paid_at} if payload.paid_at else {}),
    )
    db.add(payment)
    debt.remaining_balance = float(debt.remaining_balance) - payload.amount
    if debt.remaining_balance <= 0:
        debt.remaining_balance = 0
        debt.status = "paid"
        create_notification(db, user_id=current_user.id, title="Debt cleared",
                            message=f"🎉 {debt.name} is fully paid off!", ntype="debt")
    db.commit()
    db.refresh(debt)
    log_activity(db, user_id=current_user.id, action="repay_debt", entity="debt",
                entity_id=debt.id, ip_address=client_ip(request),
                metadata={"amount": payload.amount})
    total_paid = sum(float(p.amount) for p in debt.payments)
    return DebtWithPayments(
        **DebtResponse.model_validate(debt).model_dump(),
        total_paid=total_paid,
        payments=debt.payments,
    )

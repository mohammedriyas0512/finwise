"""
Loan calculator + loan records (home/car/education/personal/business) + comparison.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Loan
from app.schemas import LoanCreate, LoanResponse
from app.services.finance_service import calculate_emi, compare_loans
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/loans", tags=["Loan"])


@router.get("", response_model=list[LoanResponse])
def list_loans(db: DbSession, current_user: CurrentUser):
    return db.scalars(
        select(Loan).where(Loan.user_id == current_user.id).order_by(Loan.created_at.desc())
    ).all()


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate, request: Request, db: DbSession, current_user: CurrentUser):
    emi_res = calculate_emi(payload.principal, payload.interest_rate, payload.tenure_months)
    loan = Loan(
        user_id=current_user.id,
        monthly_emi=emi_res.monthly_emi,
        total_interest=emi_res.total_interest,
        total_payment=emi_res.total_payment,
        **payload.dict(),
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    log_activity(db, user_id=current_user.id, action="create_loan", entity="loan",
                entity_id=loan.id, ip_address=client_ip(request))
    return loan


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: int, db: DbSession, current_user: CurrentUser):
    loan = db.get(Loan, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_200_OK)
def delete_loan(loan_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    loan = db.get(Loan, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    db.delete(loan)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_loan", entity="loan",
                entity_id=loan_id, ip_address=client_ip(request))
    return {"message": "Loan deleted successfully"}


@router.post("/compare", tags=["Loan"])
def compare(payload: list[dict]):
    """Compare two or more loan scenarios. Each: principal, interest_rate, tenure_months, optional label."""
    if len(payload) < 2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provide at least two loans")
    try:
        return compare_loans(payload)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

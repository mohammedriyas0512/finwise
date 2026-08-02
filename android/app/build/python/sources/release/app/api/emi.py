"""
EMI calculator endpoints: live calculation + saved history + PDF export.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import EMICalculation
from app.schemas import EMICalcRecord, EMICalcRequest, EMICalcResponse
from app.services.export_service import export_pdf
from app.services.finance_service import calculate_emi
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/emi", tags=["EMI"])


@router.post("/calculate", response_model=EMICalcResponse)
def calculate(payload: EMICalcRequest):
    """Compute EMI + full amortization. Does not persist."""
    res = calculate_emi(payload.loan_amount, payload.interest_rate, payload.tenure_months)
    return EMICalcResponse(
        loan_amount=payload.loan_amount,
        interest_rate=payload.interest_rate,
        tenure_months=payload.tenure_months,
        monthly_emi=res.monthly_emi,
        total_interest=res.total_interest,
        total_payment=res.total_payment,
        amortization=res.amortization,
    )


@router.post("/save", response_model=EMICalcRecord, status_code=status.HTTP_201_CREATED)
def save_calculation(payload: EMICalcRequest, request: Request, db: DbSession, current_user: CurrentUser):
    res = calculate_emi(payload.loan_amount, payload.interest_rate, payload.tenure_months)
    record = EMICalculation(
        user_id=current_user.id,
        loan_amount=payload.loan_amount,
        interest_rate=payload.interest_rate,
        tenure_months=payload.tenure_months,
        monthly_emi=res.monthly_emi,
        total_interest=res.total_interest,
        total_payment=res.total_payment,
        amortization=json.dumps(res.amortization),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    log_activity(db, user_id=current_user.id, action="save_emi", entity="emi",
                entity_id=record.id, ip_address=client_ip(request))
    return record


@router.get("/history", response_model=list[EMICalcRecord])
def history(db: DbSession, current_user: CurrentUser, limit: int = Query(20, ge=1, le=200)):
    return db.scalars(
        select(EMICalculation).where(EMICalculation.user_id == current_user.id)
        .order_by(EMICalculation.created_at.desc()).limit(limit)
    ).all()


@router.get("/export/{calc_id}/pdf")
def export_pdf_report(calc_id: int, db: DbSession, current_user: CurrentUser):
    record = db.get(EMICalculation, calc_id)
    if not record or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    schedule = json.loads(record.amortization or "[]")
    rows = [
        {
            "month": r["month"],
            "payment": r["payment"],
            "principal": r["principal"],
            "interest": r["interest"],
            "balance": r["balance"],
        }
        for r in schedule
    ]
    path = export_pdf(
        title="FinWise EMI Amortization Schedule",
        columns=["month", "payment", "principal", "interest", "balance"],
        rows=rows,
        prefix="emi_schedule",
        summary=[
            ("Loan Amount", f"{record.loan_amount:,.2f}"),
            ("Interest Rate", f"{record.interest_rate}%"),
            ("Tenure (months)", str(record.tenure_months)),
            ("Monthly EMI", f"{record.monthly_emi:,.2f}"),
            ("Total Interest", f"{record.total_interest:,.2f}"),
            ("Total Payment", f"{record.total_payment:,.2f}"),
        ],
    )
    return FileResponse(path, filename="emi_schedule.pdf", media_type="application/pdf")

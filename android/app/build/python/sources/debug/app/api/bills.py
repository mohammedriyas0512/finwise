"""
Recurring expense / bill reminder endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import BillReminder
from app.schemas import BillCreate, BillResponse, BillUpdate
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/bills", tags=["Recurring Expenses"])


@router.get("", response_model=list[BillResponse])
def list_bills(db: DbSession, current_user: CurrentUser, active_only: bool = False):
    stmt = select(BillReminder).where(BillReminder.user_id == current_user.id)
    if active_only:
        stmt = stmt.where(BillReminder.is_active.is_(True))
    stmt = stmt.order_by(BillReminder.due_day.asc())
    return db.scalars(stmt).all()


@router.post("", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(payload: BillCreate, request: Request, db: DbSession, current_user: CurrentUser):
    bill = BillReminder(user_id=current_user.id, **payload.dict())
    db.add(bill)
    db.commit()
    db.refresh(bill)
    log_activity(db, user_id=current_user.id, action="create_bill", entity="bill",
                entity_id=bill.id, ip_address=client_ip(request))
    return bill


@router.patch("/{bill_id}", response_model=BillResponse)
def update_bill(bill_id: int, payload: BillUpdate, request: Request, db: DbSession, current_user: CurrentUser):
    bill = db.get(BillReminder, bill_id)
    if not bill or bill.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(bill, field, value)
    db.commit()
    db.refresh(bill)
    log_activity(db, user_id=current_user.id, action="update_bill", entity="bill",
                entity_id=bill.id, ip_address=client_ip(request))
    return bill


@router.delete("/{bill_id}", status_code=status.HTTP_200_OK)
def delete_bill(bill_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    bill = db.get(BillReminder, bill_id)
    if not bill or bill.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    db.delete(bill)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_bill", entity="bill",
                entity_id=bill_id, ip_address=client_ip(request))
    return {"message": "Bill reminder deleted successfully"}

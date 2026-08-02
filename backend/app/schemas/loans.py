"""
Pydantic schemas for loans, EMI calculations, debts, savings goals, and bill reminders.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Loan -------------------------------------------------------------------
class LoanBase(BaseModel):
    loan_type: str = Field(..., pattern="^(home|car|education|personal|business)$")
    principal: float = Field(..., gt=0, le=1_000_000_000)
    interest_rate: float = Field(..., ge=0, le=100)
    tenure_months: int = Field(..., gt=0, le=600)
    start_date: Optional[datetime] = None
    notes: Optional[str] = None


class LoanCreate(LoanBase):
    pass


class LoanResponse(LoanBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    monthly_emi: float
    total_interest: float
    total_payment: float
    created_at: datetime


# --- EMI calculation --------------------------------------------------------
class EMICalcRequest(BaseModel):
    loan_amount: float = Field(..., gt=0, le=1_000_000_000)
    interest_rate: float = Field(..., ge=0, le=100)
    tenure_months: int = Field(..., gt=0, le=600)


class AmortizationRow(BaseModel):
    month: int
    payment: float
    principal: float
    interest: float
    balance: float


class EMICalcResponse(BaseModel):
    loan_amount: float
    interest_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_payment: float
    amortization: list[AmortizationRow]


class EMICalcRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    loan_amount: float
    interest_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_payment: float
    created_at: datetime


# --- Debt -------------------------------------------------------------------
class DebtBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    debt_type: str = Field(..., pattern="^(credit_card|personal_loan|borrowed|bank_loan|friend_loan)$")
    total_amount: float = Field(..., gt=0, le=1_000_000_000)
    remaining_balance: float = Field(..., ge=0, le=1_000_000_000)
    monthly_payment: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    status: str = Field("active", pattern="^(active|paid|overdue)$")
    notes: Optional[str] = None


class DebtCreate(DebtBase):
    pass


class DebtUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    debt_type: Optional[str] = Field(None, pattern="^(credit_card|personal_loan|borrowed|bank_loan|friend_loan)$")
    total_amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)
    remaining_balance: Optional[float] = Field(None, ge=0, le=1_000_000_000)
    monthly_payment: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(active|paid|overdue)$")
    notes: Optional[str] = None


class DebtResponse(DebtBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# --- Debt payments (repayment history) --------------------------------------
class DebtPaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, le=1_000_000_000)
    note: Optional[str] = Field(None, max_length=255)
    paid_at: Optional[datetime] = None


class DebtPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    debt_id: int
    user_id: int
    amount: float
    note: Optional[str] = None
    paid_at: datetime
    created_at: datetime


class DebtWithPayments(DebtResponse):
    total_paid: float
    payments: list[DebtPaymentResponse] = []


# --- Savings goal -----------------------------------------------------------
class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    target_amount: float = Field(..., gt=0, le=1_000_000_000)
    current_amount: float = Field(0, ge=0, le=1_000_000_000)
    deadline: Optional[datetime] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    target_amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)
    current_amount: Optional[float] = Field(None, ge=0, le=1_000_000_000)
    deadline: Optional[datetime] = None


class GoalResponse(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    progress_percent: float
    remaining_amount: float
    created_at: datetime
    updated_at: datetime


# --- Bill reminder ----------------------------------------------------------
class BillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=60)
    amount: float = Field(..., gt=0, le=1_000_000_000)
    due_day: int = Field(..., ge=1, le=31)
    is_recurring: bool = True
    is_active: bool = True
    notes: Optional[str] = None


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = Field(None, min_length=1, max_length=60)
    amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)
    due_day: Optional[int] = Field(None, ge=1, le=31)
    is_recurring: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class BillResponse(BillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime

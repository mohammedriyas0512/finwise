"""
Pydantic schemas for income, expense, transaction, category, and budget modules.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Categories -------------------------------------------------------------
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    type: str = Field(..., regex="^(income|expense)$")


class CategoryResponse(BaseModel):
    class Config:
        orm_mode = True

    id: int
    user_id: Optional[int] = None
    name: str
    type: str
    is_default: bool
    created_at: datetime


# --- Income -----------------------------------------------------------------
class IncomeBase(BaseModel):
    amount: float = Field(..., gt=0, le=1_000_000_000)
    category: str = Field(..., min_length=1, max_length=60)
    description: Optional[str] = Field(None, max_length=255)
    frequency: str = Field("one_time", regex="^(monthly|weekly|one_time)$")
    date: datetime


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)
    category: Optional[str] = Field(None, min_length=1, max_length=60)
    description: Optional[str] = Field(None, max_length=255)
    frequency: Optional[str] = Field(None, regex="^(monthly|weekly|one_time)$")
    date: Optional[datetime] = None


class IncomeResponse(IncomeBase):
    class Config:
        orm_mode = True

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# --- Expense ----------------------------------------------------------------
class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, le=1_000_000_000)
    category: str = Field(..., min_length=1, max_length=60)
    description: Optional[str] = Field(None, max_length=255)
    payment_method: Optional[str] = Field(None, max_length=30)
    date: datetime


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)
    category: Optional[str] = Field(None, min_length=1, max_length=60)
    description: Optional[str] = Field(None, max_length=255)
    payment_method: Optional[str] = Field(None, max_length=30)
    date: Optional[datetime] = None


class ExpenseResponse(ExpenseBase):
    class Config:
        orm_mode = True

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# --- Transaction (read-only mirror for global search) ------------------------
class TransactionResponse(BaseModel):
    class Config:
        orm_mode = True

    id: int
    user_id: int
    txn_type: str
    amount: float
    category: str
    description: Optional[str] = None
    date: datetime
    reference_id: Optional[int] = None
    created_at: datetime


# --- Budget -----------------------------------------------------------------
class BudgetBase(BaseModel):
    month: str = Field(..., regex=r"^\d{4}-\d{2}$")
    category: str = Field(..., min_length=1, max_length=60)
    limit_amount: float = Field(..., gt=0, le=1_000_000_000)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    limit_amount: Optional[float] = Field(None, gt=0, le=1_000_000_000)


class BudgetResponse(BudgetBase):
    class Config:
        orm_mode = True

    id: int
    user_id: int
    spent_amount: float
    remaining: float
    usage_percent: float
    created_at: datetime
    updated_at: datetime

"""
SQLAlchemy ORM models for FinWise.

All timestamps are stored as UTC datetime. Foreign keys link every
user-scoped record back to ``users.id`` and are indexed for query performance.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# User & auth
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False, index=True)  # user | admin
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    profile_photo = Column(String(512), nullable=True)
    currency = Column(String(10), default="INR", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    theme = Column(String(10), default="light", nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    income = relationship("Income", back_populates="owner", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="owner", cascade="all, delete-orphan")
    emi = relationship("EMICalculation", back_populates="owner", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="owner", cascade="all, delete-orphan")
    goals = relationship("SavingGoal", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
    bills = relationship("BillReminder", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="owner", cascade="all, delete-orphan")
    activity = relationship("ActivityLog", back_populates="owner", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="owner", uselist=False, cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    dark_mode = Column(Boolean, default=False, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    budget_alerts = Column(Boolean, default=True, nullable=False)
    emi_reminders = Column(Boolean, default=True, nullable=False)
    debt_reminders = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    owner = relationship("User", back_populates="settings")


# ---------------------------------------------------------------------------
# Categories (reusable lookup list, user-scoped for custom additions)
# ---------------------------------------------------------------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(60), nullable=False)
    type = Column(String(20), nullable=False, index=True)  # income | expense
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", "type", name="uq_category_user_name_type"),
    )

    owner = relationship("User", back_populates="categories")


# Wire the categories relationship onto User (defined after Category exists).
User.categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Income & Expenses
# ---------------------------------------------------------------------------
class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String(60), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    frequency = Column(String(20), default="one_time", nullable=False)  # monthly|weekly|one_time
    date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    owner = relationship("User", back_populates="income")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String(60), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    payment_method = Column(String(30), nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    owner = relationship("User", back_populates="expenses")


# Unified transaction view (income + expense mirror) for fast global search.
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    txn_type = Column(String(20), nullable=False, index=True)  # income | expense
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String(60), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    reference_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    owner = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "date"),
        Index("ix_transactions_user_type_cat", "user_id", "txn_type", "category"),
    )


# ---------------------------------------------------------------------------
# Loans & EMI
# ---------------------------------------------------------------------------
class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_type = Column(String(40), nullable=False, index=True)  # home|car|education|personal|business
    principal = Column(Numeric(14, 2), nullable=False)
    interest_rate = Column(Numeric(6, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    monthly_emi = Column(Numeric(14, 2), nullable=False)
    total_interest = Column(Numeric(14, 2), nullable=False)
    total_payment = Column(Numeric(14, 2), nullable=False)
    start_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    owner = relationship("User", back_populates="loans")


class EMICalculation(Base):
    __tablename__ = "emi_calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_amount = Column(Numeric(14, 2), nullable=False)
    interest_rate = Column(Numeric(6, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    monthly_emi = Column(Numeric(14, 2), nullable=False)
    total_interest = Column(Numeric(14, 2), nullable=False)
    total_payment = Column(Numeric(14, 2), nullable=False)
    amortization = Column(Text, nullable=True)  # JSON string of schedule rows
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    owner = relationship("User", back_populates="emi")


# ---------------------------------------------------------------------------
# Debt tracker
# ---------------------------------------------------------------------------
class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    debt_type = Column(String(40), nullable=False, index=True)  # credit_card|personal_loan|borrowed|bank_loan|friend_loan
    total_amount = Column(Numeric(14, 2), nullable=False)
    remaining_balance = Column(Numeric(14, 2), nullable=False)
    monthly_payment = Column(Numeric(14, 2), nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", nullable=False, index=True)  # active|paid|overdue
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    owner = relationship("User", back_populates="debts")
    payments = relationship(
        "DebtPayment",
        back_populates="debt",
        cascade="all, delete-orphan",
        order_by="DebtPayment.paid_at.desc()",
    )


class DebtPayment(Base):
    """A single repayment made against a Debt."""

    __tablename__ = "debt_payments"

    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(Integer, ForeignKey("debts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    note = Column(String(255), nullable=True)
    paid_at = Column(DateTime, default=_utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    debt = relationship("Debt", back_populates="payments")


# ---------------------------------------------------------------------------
# Savings goals
# ---------------------------------------------------------------------------
class SavingGoal(Base):
    __tablename__ = "saving_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    target_amount = Column(Numeric(14, 2), nullable=False)
    current_amount = Column(Numeric(14, 2), default=0, nullable=False)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    owner = relationship("User", back_populates="goals")


# ---------------------------------------------------------------------------
# Budgets & recurring bills
# ---------------------------------------------------------------------------
class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String(7), nullable=False, index=True)  # YYYY-MM
    category = Column(String(60), nullable=False, index=True)
    limit_amount = Column(Numeric(14, 2), nullable=False)
    spent_amount = Column(Numeric(14, 2), default=0, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "month", "category", name="uq_budget_user_month_cat"),
    )

    owner = relationship("User", back_populates="budgets")


class BillReminder(Base):
    __tablename__ = "bill_reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(60), nullable=False, index=True)  # netflix|electricity|rent|...
    amount = Column(Numeric(14, 2), nullable=False)
    due_day = Column(Integer, nullable=False)  # day of month (1-31)
    is_recurring = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    owner = relationship("User", back_populates="bills")


# ---------------------------------------------------------------------------
# Notifications, reports, activity logs
# ---------------------------------------------------------------------------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(40), default="info", nullable=False, index=True)  # budget|emi|debt|goal|recurring
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    owner = relationship("User", back_populates="notifications")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(40), nullable=False, index=True)  # daily|weekly|monthly|yearly|income|expense|savings|debt|budget
    period = Column(String(20), nullable=True)
    generated_at = Column(DateTime, default=_utcnow, nullable=False)
    file_path = Column(String(512), nullable=True)
    format = Column(String(10), default="pdf", nullable=False)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    action = Column(String(120), nullable=False)
    entity = Column(String(60), nullable=True)
    entity_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    meta = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    owner = relationship("User", back_populates="activity")


__all__ = [
    "Base",
    "User",
    "UserSettings",
    "Category",
    "Income",
    "Expense",
    "Transaction",
    "Loan",
    "EMICalculation",
    "Debt",
    "DebtPayment",
    "SavingGoal",
    "Budget",
    "BillReminder",
    "Notification",
    "Report",
    "ActivityLog",
]

"""
Aggregation helpers for dashboard, charts and financial health.

All functions are pure given a DB session + user; they return plain dicts so
routers stay thin and the response shapes are consistent for the frontend.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Budget,
    Debt,
    EMICalculation,
    Expense,
    Income,
    Loan,
    SavingGoal,
    Transaction,
)
from app.services.finance_service import calculate_emi
from app.services.health_service import calculate_health_score
from app.utils.helpers import month_key


def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    return start, end


def current_month_bounds() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    return _month_bounds(now.year, now.month)


def dashboard_summary(db: Session, user_id: int) -> dict:
    now = datetime.now(timezone.utc)
    m_start, m_end = current_month_bounds()

    total_income = float(db.scalar(select(func.coalesce(func.sum(Income.amount), 0)).where(Income.user_id == user_id)) or 0)
    total_expense = float(db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.user_id == user_id)) or 0)
    monthly_income = float(db.scalar(
        select(func.coalesce(func.sum(Income.amount), 0))
        .where(Income.user_id == user_id, Income.date >= m_start, Income.date < m_end)
    ) or 0)
    monthly_expense = float(db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(Expense.user_id == user_id, Expense.date >= m_start, Expense.date < m_end)
    ) or 0)

    total_savings = total_income - total_expense
    total_debt = float(db.scalar(
        select(func.coalesce(func.sum(Debt.remaining_balance), 0))
        .where(Debt.user_id == user_id, Debt.status != "paid")
    ) or 0)
    total_goals_current = float(db.scalar(
        select(func.coalesce(func.sum(SavingGoal.current_amount), 0)).where(SavingGoal.user_id == user_id)
    ) or 0)
    total_goals_target = float(db.scalar(
        select(func.coalesce(func.sum(SavingGoal.target_amount), 0)).where(SavingGoal.user_id == user_id)
    ) or 0)

    # Monthly EMI from saved EMI calculations + active loans.
    emi_sum = float(db.scalar(
        select(func.coalesce(func.sum(Loan.monthly_emi), 0)).where(Loan.user_id == user_id)
    ) or 0)

    balance = total_income - total_expense - total_debt

    # Upcoming EMI / due payments (next 30 days). We approximate due EMIs from
    # loans without explicit due dates, plus debt due dates in range.
    soon = now + timedelta(days=30)
    upcoming_debts = db.scalars(
        select(Debt).where(
            Debt.user_id == user_id,
            Debt.status != "paid",
            Debt.due_date.isnot(None),
            Debt.due_date >= now,
            Debt.due_date <= soon,
        ).order_by(Debt.due_date.asc())
    ).all()

    # Budget usage for health scoring.
    budgets = db.scalars(select(Budget).where(Budget.user_id == user_id)).all()
    if budgets:
        total_limit = sum(float(b.limit_amount) for b in budgets)
        total_spent = sum(float(b.spent_amount) for b in budgets)
        budget_usage = (total_spent / total_limit) * 100 if total_limit > 0 else 0.0
    else:
        budget_usage = 0.0

    health = calculate_health_score(
        total_income=total_income,
        total_expense=total_expense,
        total_savings=total_savings,
        total_debt=total_debt,
        total_emi=emi_sum,
        budget_usage_percent=budget_usage,
    )

    recent = db.scalars(
        select(Transaction).where(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc()).limit(8)
    ).all()

    goals = db.scalars(
        select(SavingGoal).where(SavingGoal.user_id == user_id).order_by(SavingGoal.deadline.asc())
    ).all()

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "monthly_income": round(monthly_income, 2),
        "monthly_expense": round(monthly_expense, 2),
        "total_savings": round(total_savings, 2),
        "total_debt": round(total_debt, 2),
        "total_emi": round(emi_sum, 2),
        "current_balance": round(balance, 2),
        "goals_current": round(total_goals_current, 2),
        "goals_target": round(total_goals_target, 2),
        "financial_health": {
            "score": health.score,
            "rating": health.rating,
            "factors": [f.__dict__ for f in health.factors],
        },
        "recent_transactions": [
            {
                "id": t.id, "type": t.txn_type, "amount": float(t.amount),
                "category": t.category, "description": t.description, "date": t.date,
            } for t in recent
        ],
        "upcoming_debts": [
            {
                "id": d.id, "name": d.name, "remaining_balance": float(d.remaining_balance),
                "due_date": d.due_date, "monthly_payment": float(d.monthly_payment) if d.monthly_payment else 0,
            } for d in upcoming_debts
        ],
        "savings_goals": [
            {
                "id": g.id, "name": g.name, "target_amount": float(g.target_amount),
                "current_amount": float(g.current_amount),
                "progress_percent": round((float(g.current_amount) / float(g.target_amount)) * 100, 1) if g.target_amount else 0,
                "deadline": g.deadline,
            } for g in goals
        ],
    }


def expense_chart(db: Session, user_id: int) -> dict:
    """Category-wise expense totals for the current user (all time)."""
    rows = db.execute(
        select(Expense.category, func.sum(Expense.amount))
        .where(Expense.user_id == user_id)
        .group_by(Expense.category)
    ).all()
    return {
        "labels": [r[0] for r in rows],
        "values": [round(float(r[1]), 2) for r in rows],
    }


def income_chart(db: Session, user_id: int) -> dict:
    rows = db.execute(
        select(Income.category, func.sum(Income.amount))
        .where(Income.user_id == user_id)
        .group_by(Income.category)
    ).all()
    return {
        "labels": [r[0] for r in rows],
        "values": [round(float(r[1]), 2) for r in rows],
    }


def monthly_analysis(db: Session, user_id: int, months: int = 6) -> dict:
    """Income vs expense per month for the last N months (date-based)."""
    now = datetime.now(timezone.utc)
    labels, income_vals, expense_vals = [], [], []
    for i in range(months - 1, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        start, end = _month_bounds(y, m)
        mk = month_key(start)
        labels.append(mk)
        inc = float(db.scalar(
            select(func.coalesce(func.sum(Income.amount), 0))
            .where(Income.user_id == user_id, Income.date >= start, Income.date < end)
        ) or 0)
        exp = float(db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(Expense.user_id == user_id, Expense.date >= start, Expense.date < end)
        ) or 0)
        income_vals.append(round(inc, 2))
        expense_vals.append(round(exp, 2))
    return {"labels": labels, "income": income_vals, "expense": expense_vals}


def savings_trend(db: Session, user_id: int, months: int = 6) -> dict:
    """Cumulative savings (income - expense) per month."""
    data = monthly_analysis(db, user_id, months)
    cumulative = 0.0
    trend = []
    for inc, exp in zip(data["income"], data["expense"]):
        cumulative += (inc - exp)
        trend.append(round(cumulative, 2))
    return {"labels": data["labels"], "savings": trend}

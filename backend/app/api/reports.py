"""
Reports endpoints: built-on-the-fly reports for daily/weekly/monthly/yearly
and income/expense/savings/debt/budget, with PDF / Excel / CSV export.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Debt, Expense, Income, SavingGoal, Transaction
from app.schemas import ReportCreate
from app.services.export_service import export_csv, export_excel, export_pdf
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/reports", tags=["Reports"])


def _period_bounds(report_type: str, reference: datetime | None = None) -> tuple[datetime, datetime]:
    now = reference or datetime.now(timezone.utc)
    if report_type == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif report_type == "weekly":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif report_type == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    elif report_type == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=start.year + 1)
    else:
        # category-style reports use all-time bounds.
        start = datetime(2000, 1, 1, tzinfo=timezone.utc)
        end = now + timedelta(days=1)
    return start, end


def _rows_for_period(db: Session, user_id: int, start: datetime, end: datetime) -> list[dict]:
    txns = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.date >= start,
            Transaction.date < end,
        ).order_by(Transaction.date.desc())
    ).all()
    return [
        {
            "date": t.date.strftime("%Y-%m-%d"),
            "type": t.txn_type,
            "category": t.category,
            "amount": float(t.amount),
            "description": t.description or "",
        } for t in txns
    ]


@router.post("/generate")
def generate_report(payload: ReportCreate, request: Request, db: DbSession, current_user: CurrentUser):
    start, end = _period_bounds(payload.report_type)
    rows = _rows_for_period(db, current_user.id, start, end)

    title_map = {
        "daily": "Daily Report", "weekly": "Weekly Report", "monthly": "Monthly Report",
        "yearly": "Yearly Report", "income": "Income Report", "expense": "Expense Report",
        "savings": "Savings Report", "debt": "Debt Report", "budget": "Budget Report",
    }

    summary = _summary_block(db, current_user.id, payload.report_type, start, end)

    if payload.format == "pdf":
        path = export_pdf(title_map[payload.report_type], ["date", "type", "category", "amount", "description"],
                          rows, prefix=f"report_{payload.report_type}", summary=summary)
        media = "application/pdf"
        fname = f"{payload.report_type}_report.pdf"
    elif payload.format == "excel":
        path = export_excel(rows, ["date", "type", "category", "amount", "description"],
                            prefix=f"report_{payload.report_type}", sheet_name=title_map[payload.report_type])
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        fname = f"{payload.report_type}_report.xlsx"
    else:
        path = export_csv(rows, ["date", "type", "category", "amount", "description"],
                          prefix=f"report_{payload.report_type}")
        media = "text/csv"
        fname = f"{payload.report_type}_report.csv"

    log_activity(db, user_id=current_user.id, action="generate_report",
                 entity="report", ip_address=client_ip(request),
                 metadata={"type": payload.report_type, "format": payload.format})
    return FileResponse(path, filename=fname, media_type=media)


@router.get("/preview")
def preview_report(db: DbSession, current_user: CurrentUser,
                  report_type: str = Query("monthly", pattern="^(daily|weekly|monthly|yearly|income|expense|savings|debt|budget)$")):
    start, end = _period_bounds(report_type)
    rows = _rows_for_period(db, current_user.id, start, end)
    summary = _summary_block(db, current_user.id, report_type, start, end)
    return {"report_type": report_type, "period_start": start, "period_end": end,
            "summary": summary, "rows": rows, "count": len(rows)}


def _summary_block(db: Session, user_id: int, report_type: str, start: datetime, end: datetime) -> list[tuple[str, str]]:
    if report_type == "debt":
        debts = db.scalars(select(Debt).where(Debt.user_id == user_id, Debt.status != "paid")).all()
        total_remaining = sum(float(d.remaining_balance) for d in debts)
        return [("Active Debts", str(len(debts))), ("Total Remaining", f"{total_remaining:,.2f}")]
    if report_type == "savings":
        goals = db.scalars(select(SavingGoal).where(SavingGoal.user_id == user_id)).all()
        current = sum(float(g.current_amount) for g in goals)
        target = sum(float(g.target_amount) for g in goals)
        return [("Goals", str(len(goals))), ("Saved", f"{current:,.2f}"), ("Target", f"{target:,.2f}")]

    inc = float(db.scalar(
        select(func.coalesce(func.sum(Income.amount), 0))
        .where(Income.user_id == user_id, Income.date >= start, Income.date < end)
    ) or 0)
    exp = float(db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(Expense.user_id == user_id, Expense.date >= start, Expense.date < end)
    ) or 0)
    return [
        ("Total Income", f"{inc:,.2f}"),
        ("Total Expense", f"{exp:,.2f}"),
        ("Net", f"{inc - exp:,.2f}"),
    ]

"""
Aggregates all API routers under a single versioned prefix (/api).
"""
from fastapi import APIRouter

from app.api import (
    admin,
    auth,
    bills,
    budgets,
    categories,
    charts,
    dashboard,
    debts,
    emi,
    expenses,
    goals,
    health,
    income,
    loans,
    notifications,
    reports,
    transactions,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(income.router)
api_router.include_router(expenses.router)
api_router.include_router(transactions.router)
api_router.include_router(categories.router)
api_router.include_router(budgets.router)
api_router.include_router(loans.router)
api_router.include_router(emi.router)
api_router.include_router(debts.router)
api_router.include_router(goals.router)
api_router.include_router(bills.router)
api_router.include_router(notifications.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
api_router.include_router(charts.router)
api_router.include_router(health.router)
api_router.include_router(admin.router)

"""
Financial Health Score calculation.

Returns a 0-100 score plus a rating band and the contributing factors so the
UI can explain *why* a user received a given score.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HealthFactor:
    label: str
    score: float  # 0-100 contribution (already weighted)
    detail: str


@dataclass
class HealthResult:
    score: int  # 0-100 rounded
    rating: str  # poor | average | good | excellent
    factors: list[HealthFactor] = field(default_factory=list)

    @staticmethod
    def rating_for(score: int) -> str:
        if score >= 80:
            return "Excellent"
        if score >= 60:
            return "Good"
        if score >= 40:
            return "Average"
        return "Poor"


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def calculate_health_score(
    total_income: float,
    total_expense: float,
    total_savings: float,
    total_debt: float,
    total_emi: float,
    budget_usage_percent: float,
) -> HealthResult:
    """Weighted multi-factor scoring.

    Weights (sum to 100):
      - Savings rate (25)
      - Expense-to-income ratio (25)
      - Debt-to-income ratio (25)
      - EMI burden vs income (15)
      - Budget discipline (10)
    """
    income = total_income or 0.0
    expense = total_expense or 0.0
    savings = total_savings or 0.0
    debt = total_debt or 0.0
    emi = total_emi or 0.0

    factors: list[HealthFactor] = []

    # 1. Savings rate = savings / income (cap at 50% as "ideal")
    if income > 0:
        savings_rate = savings / income
    else:
        savings_rate = 0.0
    # 50% savings -> full marks.
    savings_score = _clamp((savings_rate / 0.5) * 100)
    factors.append(HealthFactor(
        "Savings Rate",
        round(savings_score * 0.25, 1),
        f"{savings_rate * 100:.0f}% of income saved",
    ))

    # 2. Expense-to-income ratio. Lower is better. 100% expense -> 0.
    if income > 0:
        expense_ratio = expense / income
    else:
        expense_ratio = 1.0 if expense > 0 else 0.0
    expense_score = _clamp((1 - expense_ratio) * 100)
    factors.append(HealthFactor(
        "Expense Control",
        round(expense_score * 0.25, 1),
        f"{expense_ratio * 100:.0f}% of income spent",
    ))

    # 3. Debt-to-income ratio (annualised debts vs monthly income * 12).
    #    Ideal: total debt <= 3x annual income ish. We treat >6x annual income as max risk.
    annual_income = income * 12
    if annual_income > 0:
        debt_ratio = debt / annual_income
    else:
        debt_ratio = 1.0 if debt > 0 else 0.0
    # 0 debt -> 100; debt = 6x annual income -> 0.
    debt_score = _clamp(100 - (debt_ratio / 6.0) * 100)
    factors.append(HealthFactor(
        "Debt Load",
        round(debt_score * 0.25, 1),
        f"Debt is {debt_ratio * 100:.0f}% of annual income",
    ))

    # 4. EMI burden vs income. EMI/income < 30% -> full marks, >60% -> 0.
    if income > 0:
        emi_ratio = emi / income
    else:
        emi_ratio = 1.0 if emi > 0 else 0.0
    emi_score = _clamp(100 - ((emi_ratio - 0.30) / 0.30) * 100)
    factors.append(HealthFactor(
        "EMI Burden",
        round(emi_score * 0.15, 1),
        f"EMI is {emi_ratio * 100:.0f}% of income",
    ))

    # 5. Budget discipline. Under 100% usage -> full, 150%+ -> 0.
    usage = budget_usage_percent or 0.0
    budget_score = _clamp(100 - ((usage - 100.0) / 50.0) * 100)
    factors.append(HealthFactor(
        "Budget Discipline",
        round(budget_score * 0.10, 1),
        f"{usage:.0f}% of budget used",
    ))

    raw = sum(f.score for f in factors)
    final = int(round(_clamp(raw, 0, 100)))

    return HealthResult(
        score=final,
        rating=HealthResult.rating_for(final),
        factors=factors,
    )

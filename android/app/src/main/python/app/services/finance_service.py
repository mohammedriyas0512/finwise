"""
Pure financial calculation helpers (no DB / IO side effects).

Kept deterministic and side-effect free so they are easy to unit test.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EMIResult:
    monthly_emi: float
    total_interest: float
    total_payment: float
    amortization: list[dict]


def calculate_emi(
    principal: float,
    annual_rate_percent: float,
    tenure_months: int,
) -> EMIResult:
    """Standard reducing-balance EMI with full amortization schedule."""
    if principal <= 0 or tenure_months <= 0:
        raise ValueError("Principal and tenure must be greater than zero.")

    monthly_rate = (annual_rate_percent / 100.0) / 12.0
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        factor = (1 + monthly_rate) ** tenure_months
        emi = principal * monthly_rate * factor / (factor - 1)

    emi = round(emi, 2)

    balance = principal
    total_interest = 0.0
    schedule: list[dict] = []
    for month in range(1, tenure_months + 1):
        interest = round(balance * monthly_rate, 2)
        principal_part = round(emi - interest, 2)
        # Adjust final payment so the balance lands exactly on zero.
        if month == tenure_months:
            principal_part = round(balance, 2)
            emi_month = round(principal_part + interest, 2)
        else:
            emi_month = emi
        balance = round(balance - principal_part, 2)
        if balance < 0:
            balance = 0.0
        total_interest += interest
        schedule.append(
            {
                "month": month,
                "payment": emi_month,
                "principal": principal_part,
                "interest": interest,
                "balance": balance,
            }
        )

    total_interest = round(total_interest, 2)
    total_payment = round(principal + total_interest, 2)

    return EMIResult(
        monthly_emi=emi,
        total_interest=total_interest,
        total_payment=total_payment,
        amortization=schedule,
    )


def compare_loans(
    loans: list[dict],
) -> list[dict]:
    """Compare multiple loan scenarios. Each dict needs principal, rate, tenure."""
    results = []
    for loan in loans:
        res = calculate_emi(
            loan["principal"], loan["interest_rate"], loan["tenure_months"]
        )
        results.append(
            {
                "label": loan.get("label", f"Loan {len(results) + 1}"),
                "principal": loan["principal"],
                "interest_rate": loan["interest_rate"],
                "tenure_months": loan["tenure_months"],
                "monthly_emi": res.monthly_emi,
                "total_interest": res.total_interest,
                "total_payment": res.total_payment,
            }
        )
    return results


DEFAULT_INCOME_CATEGORIES = [
    "Salary", "Business", "Freelancing", "Investment", "Rental", "Gift", "Other",
]
DEFAULT_EXPENSE_CATEGORIES = [
    "Food", "Fuel", "Rent", "Electricity", "Water", "Internet", "Education",
    "Medical", "Travel", "Entertainment", "Shopping", "Insurance", "Others",
]

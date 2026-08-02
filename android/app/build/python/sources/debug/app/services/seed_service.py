"""
Seed default categories and the first admin user on startup.

Idempotent: safe to call on every boot. Categories are global defaults
(user_id NULL) shared by all users; admins are only seeded when the table is
empty so we never clobber existing accounts.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.config import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_NAME,
    DEFAULT_ADMIN_PASSWORD,
)
from app.models import Category, User


def seed_default_categories(db: Session) -> None:
    existing = db.scalar(select(func.count()).select_from(Category).where(Category.is_default.is_(True)))
    if existing:
        return

    from app.services.finance_service import DEFAULT_EXPENSE_CATEGORIES, DEFAULT_INCOME_CATEGORIES

    for name in DEFAULT_INCOME_CATEGORIES:
        db.add(Category(name=name, type="income", is_default=True))
    for name in DEFAULT_EXPENSE_CATEGORIES:
        db.add(Category(name=name, type="expense", is_default=True))
    db.commit()


def seed_admin(db: Session) -> None:
    count = db.scalar(select(func.count()).select_from(User))
    if count:
        return
    admin = User(
        full_name=DEFAULT_ADMIN_NAME,
        email=DEFAULT_ADMIN_EMAIL,
        hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
        role="admin",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(admin)
    db.commit()

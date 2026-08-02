"""
Category management endpoints.

Returns global default categories plus the user's own custom categories.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession
from app.models import Category
from app.schemas import CategoryCreate, CategoryResponse
from app.services.notification_service import log_activity
from app.utils.helpers import client_ip

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: DbSession, current_user: CurrentUser, type: str | None = None):
    stmt = select(Category).where(
        (Category.user_id == current_user.id) | (Category.is_default.is_(True))
    )
    if type:
        stmt = stmt.where(Category.type == type)
    stmt = stmt.order_by(Category.type, Category.name)
    return db.scalars(stmt).all()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, request: Request, db: DbSession, current_user: CurrentUser):
    exists = db.scalar(select(Category).where(
        (Category.user_id == current_user.id) | (Category.is_default.is_(True)),
        Category.name == payload.name,
        Category.type == payload.type,
    ))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    category = Category(user_id=current_user.id, is_default=False, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    log_activity(db, user_id=current_user.id, action="create_category", entity="category",
                entity_id=category.id, ip_address=client_ip(request))
    return category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(category_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    category = db.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if category.is_default:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Default categories cannot be deleted")
    db.delete(category)
    db.commit()
    log_activity(db, user_id=current_user.id, action="delete_category", entity="category",
                entity_id=category_id, ip_address=client_ip(request))
    return {"message": "Category deleted successfully"}

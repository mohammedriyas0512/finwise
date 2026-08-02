"""
Authentication & user account endpoints.

Covers register, login (JWT), forgot/reset password (token-free, dev-friendly),
change password, profile, settings, and account deletion.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, DbSession, get_current_user
from app.auth.security import create_access_token, hash_password, verify_password
from app.config import PASSWORD_MIN_LENGTH
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    ProfileUpdate,
    RegisterRequest,
    ResetPasswordRequest,
    SettingsUpdate,
    Token,
    UserResponse,
    UserSettingsResponse,
)
from app.services.notification_service import create_notification, log_activity
from app.services.seed_service import seed_default_categories
from app.utils.helpers import client_ip

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: DbSession):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if len(payload.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role="user",
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    seed_default_categories(db)
    log_activity(db, user_id=user.id, action="register", entity="user", ip_address=client_ip(request))
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, db: DbSession):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token = create_access_token(user.id, user.role)
    log_activity(db, user_id=user.id, action="login", entity="user", ip_address=client_ip(request))
    return Token(access_token=token, role=user.role)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(payload: ForgotPasswordRequest, db: DbSession):
    # Dev-friendly flow: reset token omitted. In production wire an email + token.
    user = db.scalar(select(User).where(User.email == payload.email))
    # Always return 200 to avoid leaking which emails exist.
    if user:
        return {"message": "If the account exists, a reset link has been sent."}
    return {"message": "If the account exists, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: DbSession):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if len(payload.new_password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters",
        )
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password has been reset successfully"}


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser):
    return current_user


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(payload: ChangePasswordRequest, request: Request, db: DbSession, current_user: CurrentUser):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if len(payload.new_password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters",
        )
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    log_activity(db, user_id=current_user.id, action="change_password", entity="user", ip_address=client_ip(request))
    return {"message": "Password updated successfully"}


@router.patch("/profile", response_model=UserResponse)
def update_profile(payload: ProfileUpdate, db: DbSession, current_user: CurrentUser):
    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(db: DbSession, current_user: CurrentUser):
    from app.models import UserSettings

    settings = db.scalar(select(UserSettings).where(UserSettings.user_id == current_user.id))
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.patch("/settings", response_model=UserSettingsResponse)
def update_settings(payload: SettingsUpdate, db: DbSession, current_user: CurrentUser):
    from app.models import UserSettings

    settings = db.scalar(select(UserSettings).where(UserSettings.user_id == current_user.id))
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings


@router.delete("/account", status_code=status.HTTP_200_OK)
def delete_account(payload: DeleteAccountRequest, request: Request, db: DbSession, current_user: CurrentUser):
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is incorrect")
    if current_user.role == "admin":
        remaining = db.scalar(select(User).where(User.role == "admin").where(User.id != current_user.id))
        if not remaining:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin account",
            )
    log_activity(db, user_id=current_user.id, action="delete_account", entity="user", ip_address=client_ip(request))
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}

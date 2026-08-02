"""
Pydantic schemas for notifications, reports, profile, settings, and misc DTOs.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


# --- Notification -----------------------------------------------------------
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


# --- Report -----------------------------------------------------------------
class ReportCreate(BaseModel):
    report_type: str = Field(
        ...,
        pattern="^(daily|weekly|monthly|yearly|income|expense|savings|debt|budget)$",
    )
    period: Optional[str] = Field(None, max_length=20)
    format: str = Field("pdf", pattern="^(pdf|excel|csv)$")


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    report_type: str
    period: Optional[str] = None
    generated_at: datetime
    file_path: Optional[str] = None
    format: str


# --- Profile / settings -----------------------------------------------------
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=120)
    phone: Optional[str] = Field(None, max_length=30)
    currency: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=10)
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")


class SettingsUpdate(BaseModel):
    dark_mode: Optional[bool] = None
    currency: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=10)
    email_notifications: Optional[bool] = None
    budget_alerts: Optional[bool] = None
    emi_reminders: Optional[bool] = None
    debt_reminders: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    dark_mode: bool
    currency: str
    language: str
    email_notifications: bool
    budget_alerts: bool
    emi_reminders: bool
    debt_reminders: bool
    created_at: datetime
    updated_at: datetime


class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)


# --- Admin ------------------------------------------------------------------
class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    ip_address: Optional[str] = None
    metadata: Optional[str] = None
    created_at: datetime


# --- Misc -------------------------------------------------------------------
class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str

import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Allowed project statuses."""

    active = "active"
    completed = "completed"
    paused = "paused"
    cancelled = "cancelled"


class ProjectBase(BaseModel):
    """Shared fields for project payloads."""

    client_id: uuid.UUID | None = Field(None, description="Optional client ID for this project.")
    name: str = Field(..., min_length=1, max_length=255, description="Project name.")
    description: str | None = Field(None, description="Optional project description.")
    status: ProjectStatus = Field(ProjectStatus.active, description="Project lifecycle status.")
    start_date: date | None = Field(None, description="Optional project start date.")
    due_date: date | None = Field(None, description="Optional project due date.")
    budget_cents: int = Field(0, ge=0, description="Project budget in cents (non-negative).")
    revenue_cents: int = Field(0, ge=0, description="Project revenue in cents (non-negative).")


class ProjectCreateRequest(ProjectBase):
    """Request body for creating a project."""


class ProjectUpdateRequest(BaseModel):
    """Request body for updating a project (all fields optional)."""

    client_id: uuid.UUID | None = Field(None, description="Optional client ID for this project.")
    name: str | None = Field(None, min_length=1, max_length=255, description="Project name.")
    description: str | None = Field(None, description="Optional project description.")
    status: ProjectStatus | None = Field(None, description="Project lifecycle status.")
    start_date: date | None = Field(None, description="Optional project start date.")
    due_date: date | None = Field(None, description="Optional project due date.")
    budget_cents: int | None = Field(None, ge=0, description="Project budget in cents (non-negative).")
    revenue_cents: int | None = Field(None, ge=0, description="Project revenue in cents (non-negative).")


class ProjectResponse(ProjectBase):
    """Response model for a project."""

    id: uuid.UUID = Field(..., description="Project ID (UUID).")
    owner_user_id: uuid.UUID = Field(..., description="Owning user ID (UUID).")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")

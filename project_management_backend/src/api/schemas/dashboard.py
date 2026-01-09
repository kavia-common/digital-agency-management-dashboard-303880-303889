import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RevenueByMonthItem(BaseModel):
    """A single month of revenue for charting."""

    month: str = Field(..., description="Month label in YYYY-MM format.")
    revenue_cents: int = Field(..., ge=0, description="Revenue for this month in cents.")


class RecentProjectItem(BaseModel):
    """Recent project summary row for the dashboard."""

    id: uuid.UUID = Field(..., description="Project ID (UUID).")
    name: str = Field(..., description="Project name.")
    client_name: str | None = Field(None, description="Client name (if project is linked to a client).")
    status: str = Field(..., description="Project status string.")
    revenue_cents: int = Field(..., ge=0, description="Project revenue in cents.")
    updated_at: datetime = Field(..., description="Project last update timestamp.")


class DashboardStatsResponse(BaseModel):
    """Response model for dashboard statistics."""

    total_active_projects: int = Field(..., ge=0, description="Count of active projects for the user.")
    total_revenue_cents: int = Field(..., ge=0, description="Total revenue across all projects for the user (cents).")
    revenue_by_month: list[RevenueByMonthItem] = Field(
        ..., description="Last 12 months of revenue totals (YYYY-MM), oldest -> newest."
    )
    recent_projects: list[RecentProjectItem] = Field(
        ..., description="Most recent projects (up to 5), ordered by updated/created time descending."
    )

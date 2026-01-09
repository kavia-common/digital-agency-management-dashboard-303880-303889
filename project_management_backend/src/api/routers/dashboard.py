from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.api.schemas.dashboard import DashboardStatsResponse, RecentProjectItem, RevenueByMonthItem
from src.db.models import Client, Project, ProjectStatus, User
from src.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _month_labels_last_12_months(now: datetime) -> list[str]:
    """Return month labels (YYYY-MM) for the last 12 months, oldest first."""
    # Use UTC to avoid timezone drift in labels.
    y = now.year
    m = now.month
    labels: list[str] = []
    for i in range(11, -1, -1):
        mm = m - i
        yy = y
        while mm <= 0:
            mm += 12
            yy -= 1
        labels.append(f"{yy:04d}-{mm:02d}")
    return labels


def _build_recent_project_item(row: Any) -> RecentProjectItem:
    """Convert a SQL row with project + client_name to API response item."""
    # Row is expected to contain: Project fields + client_name label.
    return RecentProjectItem(
        id=row.id,
        name=row.name,
        client_name=row.client_name,
        status=str(row.status),
        revenue_cents=int(row.revenue_cents or 0),
        updated_at=row.updated_at,
    )


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="Dashboard statistics",
    description=(
        "Returns dashboard KPIs for the authenticated user:\n"
        "- total_active_projects\n"
        "- total_revenue_cents\n"
        "- revenue_by_month (last 12 months)\n"
        "- recent_projects (last 5)\n"
    ),
    operation_id="dashboard_stats",
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardStatsResponse:
    """Get dashboard statistics for the authenticated user.

    Aggregations are filtered by owner_user_id, and the endpoint gracefully handles empty datasets
    by returning zeros and empty arrays.
    """
    now = datetime.now(timezone.utc)

    # Total active projects
    active_count_stmt = select(func.count()).select_from(Project).where(
        Project.owner_user_id == current_user.id,
        Project.status == ProjectStatus.active,
    )
    total_active_projects = int(db.scalar(active_count_stmt) or 0)

    # Total revenue across all projects
    total_revenue_stmt = select(func.coalesce(func.sum(Project.revenue_cents), 0)).where(
        Project.owner_user_id == current_user.id
    )
    total_revenue_cents = int(db.scalar(total_revenue_stmt) or 0)

    # Revenue by month for the last 12 months (based on created_at month).
    #
    # We intentionally use created_at here because start_date is optional and updated_at could
    # skew monthly attribution (e.g., edits months later). This provides a stable "booked by month"
    # metric suitable for a simple dashboard.
    month_key = func.to_char(Project.created_at, "YYYY-MM")
    revenue_by_month_stmt = (
        select(
            month_key.label("month"),
            func.coalesce(func.sum(Project.revenue_cents), 0).label("revenue_cents"),
        )
        .where(Project.owner_user_id == current_user.id)
        .group_by(month_key)
    )
    rows = db.execute(revenue_by_month_stmt).all()
    month_to_revenue = {r.month: int(r.revenue_cents or 0) for r in rows}

    labels = _month_labels_last_12_months(now)
    revenue_by_month = [
        RevenueByMonthItem(month=label, revenue_cents=max(0, month_to_revenue.get(label, 0))) for label in labels
    ]

    # Recent projects: include client_name via outer join.
    recency_ts = func.coalesce(Project.updated_at, Project.created_at)
    recent_stmt = (
        select(
            Project.id,
            Project.name,
            Project.status,
            Project.revenue_cents,
            Project.updated_at,
            func.coalesce(Client.name, None).label("client_name"),
        )
        .select_from(Project)
        .outerjoin(Client, Client.id == Project.client_id)
        .where(Project.owner_user_id == current_user.id)
        .order_by(desc(recency_ts))
        .limit(5)
    )
    recent_rows = db.execute(recent_stmt).all()
    recent_projects = [_build_recent_project_item(r) for r in recent_rows]

    return DashboardStatsResponse(
        total_active_projects=total_active_projects,
        total_revenue_cents=max(0, total_revenue_cents),
        revenue_by_month=revenue_by_month,
        recent_projects=recent_projects,
    )

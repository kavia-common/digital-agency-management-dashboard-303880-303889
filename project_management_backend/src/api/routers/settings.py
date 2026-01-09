from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.api.schemas.settings import ThemeResponse, ThemeUpdateRequest
from src.db.models import User, UserSettings
from src.db.session import get_db

router = APIRouter(prefix="/settings", tags=["settings"])


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@router.get(
    "/theme",
    response_model=ThemeResponse,
    summary="Get theme preference",
    description=(
        "Returns the authenticated user's persisted theme preference. "
        "If the user has no saved setting yet, returns a default of 'light'."
    ),
    operation_id="settings_get_theme",
)
def get_theme(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThemeResponse:
    """Get the current user's theme preference.

    Returns:
        ThemeResponse containing the user's theme (defaults to light if none saved).
    """
    settings_row = db.scalar(select(UserSettings).where(UserSettings.user_id == current_user.id))
    theme = (settings_row.theme if settings_row and settings_row.theme else "light").lower()
    if theme not in ("light", "dark"):
        # Defensive: if DB contains an unexpected value, fall back safely.
        theme = "light"
    return ThemeResponse(theme=theme)  # type: ignore[arg-type]


@router.put(
    "/theme",
    response_model=ThemeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update theme preference",
    description="Updates (and persists) the authenticated user's theme preference.",
    operation_id="settings_update_theme",
)
def update_theme(
    payload: ThemeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThemeResponse:
    """Update the current user's theme preference.

    This endpoint upserts a row into user_settings keyed by user_id.

    Args:
        payload: ThemeUpdateRequest with desired theme.
        db: SQLAlchemy session.
        current_user: Authenticated user from JWT.

    Returns:
        ThemeResponse with the persisted theme.
    """
    now = _utcnow()
    settings_row = db.scalar(select(UserSettings).where(UserSettings.user_id == current_user.id))
    if settings_row is None:
        settings_row = UserSettings(
            user_id=current_user.id,
            theme=str(payload.theme),
            created_at=now,
            updated_at=now,
        )
    else:
        settings_row.theme = str(payload.theme)
        settings_row.updated_at = now

    db.add(settings_row)
    db.commit()
    return ThemeResponse(theme=payload.theme)

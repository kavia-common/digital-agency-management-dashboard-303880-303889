from enum import Enum

from pydantic import BaseModel, Field


class ThemeName(str, Enum):
    """Allowed theme names for the dashboard UI."""

    light = "light"
    dark = "dark"


class ThemeResponse(BaseModel):
    """Response payload for returning the current user's theme."""

    theme: ThemeName = Field(..., description="Current theme preference for the authenticated user.")


class ThemeUpdateRequest(BaseModel):
    """Request payload for updating the current user's theme."""

    theme: ThemeName = Field(..., description="New theme preference (light or dark).")

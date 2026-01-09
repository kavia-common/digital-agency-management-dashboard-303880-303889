import uuid

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserProfile(BaseModel):
    id: uuid.UUID = Field(..., description="User ID (UUID).")
    email: EmailStr = Field(..., description="User email.")
    full_name: str | None = Field(None, description="User full name.")
    avatar_url: HttpUrl | None = Field(None, description="URL to user avatar image.")
    is_active: bool = Field(..., description="Whether the user is active.")


class UpdateUserProfileRequest(BaseModel):
    full_name: str | None = Field(None, max_length=255, description="Updated full name.")
    avatar_url: HttpUrl | None = Field(None, description="Updated avatar image URL.")

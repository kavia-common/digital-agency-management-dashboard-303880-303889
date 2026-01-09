import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    """Shared fields for client payloads."""

    name: str = Field(..., min_length=1, max_length=255, description="Client display name.")
    email: EmailStr | None = Field(None, description="Optional client email address.")
    phone: str | None = Field(None, max_length=50, description="Optional client phone number.")
    company: str | None = Field(None, max_length=255, description="Optional company name.")
    notes: str | None = Field(None, description="Optional free-form notes about the client.")


class ClientCreateRequest(ClientBase):
    """Request body for creating a client."""


class ClientUpdateRequest(BaseModel):
    """Request body for updating a client (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Client display name.")
    email: EmailStr | None = Field(None, description="Optional client email address.")
    phone: str | None = Field(None, max_length=50, description="Optional client phone number.")
    company: str | None = Field(None, max_length=255, description="Optional company name.")
    notes: str | None = Field(None, description="Optional free-form notes about the client.")


class ClientResponse(ClientBase):
    """Response model for a client."""

    id: uuid.UUID = Field(..., description="Client ID (UUID).")
    owner_user_id: uuid.UUID = Field(..., description="Owning user ID (UUID).")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")

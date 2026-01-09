from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address (used for login).")
    password: str = Field(..., min_length=8, description="User password (min 8 chars).")
    full_name: str | None = Field(None, max_length=255, description="Optional full name for the profile.")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., description="User password.")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token to be used as Bearer token.")
    token_type: str = Field("bearer", description="Token type (always 'bearer').")

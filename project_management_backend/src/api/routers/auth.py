import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from src.core.security import create_access_token, hash_password, verify_password
from src.db.models import User
from src.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up with email and password",
    description="Creates a new user account and returns a JWT access token.",
    operation_id="auth_signup",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Create a user account and return an access token."""
    existing = db.scalar(select(User).where(func.lower(User.email) == func.lower(payload.email)))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        avatar_url=None,
        is_active=True,
    )
    db.add(user)
    db.commit()

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email and password",
    description="Verifies credentials and returns a JWT access token.",
    operation_id="auth_login",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return an access token."""
    user = db.scalar(select(User).where(func.lower(User.email) == func.lower(payload.email)))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)

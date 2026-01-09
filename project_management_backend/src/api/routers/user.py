from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.api.schemas.user import UpdateUserProfileRequest, UserProfile
from src.db.models import User
from src.db.session import get_db

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user's profile",
    description="Returns the authenticated user's profile information.",
    operation_id="user_get_me",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfile:
    """Get the current authenticated user's profile."""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
    )


@router.put(
    "/me",
    response_model=UserProfile,
    summary="Update current user's profile",
    description="Updates the authenticated user's full name and/or avatar URL.",
    operation_id="user_update_me",
)
def update_me(
    payload: UpdateUserProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    """Update the current authenticated user's profile."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.avatar_url is not None:
        current_user.avatar_url = str(payload.avatar_url)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
    )

"""
Auth API Routes
Handles signup, login, refresh, and user profile management using Supabase GoTrue.
"""

import logging
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.dependencies import get_auth_service
from app.models.auth import SignUpRequest, LoginRequest, RefreshRequest, UpdateProfileRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
async def sign_up(body: SignUpRequest, auth_service=Depends(get_auth_service)):
    """Register a new family member account."""
    return auth_service.sign_up(body.email, body.password, body.display_name, body.phone)

@router.post("/login")
async def login(body: LoginRequest, auth_service=Depends(get_auth_service)):
    """Authenticate a user with email and password."""
    return auth_service.sign_in(body.email, body.password)

@router.post("/refresh")
async def refresh_token(body: RefreshRequest, auth_service=Depends(get_auth_service)):
    """Refresh an expired access token using the refresh token."""
    return auth_service.refresh_token(body.refresh_token)

@router.get("/me")
async def get_my_profile(
    user = Depends(get_current_user),
    auth_service = Depends(get_auth_service)
):
    """Get the currently authenticated user's profile information."""
    return auth_service.get_profile(user.id, user.email)

@router.put("/me")
async def update_my_profile(
    body: UpdateProfileRequest, 
    user = Depends(get_current_user),
    auth_service = Depends(get_auth_service)
):
    """Update the user's profile information."""
    return auth_service.update_profile(user.id, body.model_dump(exclude_unset=True))

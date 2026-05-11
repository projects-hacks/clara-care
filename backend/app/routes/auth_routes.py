"""
Auth API Routes
Handles signup, login, refresh, and user profile management using Supabase GoTrue.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.auth import get_auth_client, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# --- Request Models ---

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None


# --- Endpoints ---

@router.post("/signup")
async def sign_up(body: SignUpRequest):
    """
    Register a new family member account.
    Creates a user in auth.users and triggers the profiles table creation.
    """
    client = get_auth_client()
    try:
        response = client.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {
                "data": {
                    "display_name": body.display_name,
                    "phone": body.phone
                }
            }
        })
        
        return {
            "success": True,
            "user": response.user.model_dump() if response.user else None,
            "session": response.session.model_dump() if response.session else None,
            "message": "Registration successful"
        }
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(body: LoginRequest):
    """
    Authenticate a user with email and password.
    Returns access_token (JWT) and refresh_token.
    """
    client = get_auth_client()
    try:
        response = client.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password
        })
        
        if not response.session:
            raise ValueError("No session returned")
            
        return {
            "success": True,
            "user": response.user.model_dump() if response.user else None,
            "session": response.session.model_dump(),
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/refresh")
async def refresh_token(body: RefreshRequest):
    """
    Refresh an expired access token using the refresh token.
    """
    client = get_auth_client()
    try:
        response = client.auth.refresh_session(body.refresh_token)
        if not response.session:
            raise ValueError("Invalid refresh token")
            
        return {
            "success": True,
            "session": response.session.model_dump()
        }
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not refresh token")


@router.get("/me")
async def get_my_profile(user = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile information.
    """
    # Fetch from the profiles table to get the custom data
    client = get_auth_client()
    try:
        # We use the anon client, but we must pass the user's JWT to respect RLS
        # For simplicity, we can just use the user object from get_current_user
        # and fetch their public.profiles row.
        
        response = client.table("profiles").select("*").eq("id", user.id).execute()
        
        profile = response.data[0] if response.data else {}
        
        return {
            "id": user.id,
            "email": user.email,
            "profile": profile,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    except Exception as e:
        logger.error(f"Failed to fetch profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not fetch profile")


@router.put("/me")
async def update_my_profile(body: UpdateProfileRequest, user = Depends(get_current_user)):
    """
    Update the user's profile information (display_name, phone).
    """
    client = get_auth_client()
    try:
        updates = {}
        if body.display_name is not None:
            updates["display_name"] = body.display_name
        if body.phone is not None:
            updates["phone"] = body.phone
            
        if not updates:
            return {"success": True, "message": "No changes requested"}
            
        response = client.table("profiles").update(updates).eq("id", user.id).execute()
        
        # Also try to sync with auth.users metadata for consistency
        try:
            client.auth.update_user({
                "data": updates
            })
        except Exception as e:
            logger.warning(f"Could not update auth user metadata: {e}")
            
        return {
            "success": True,
            "profile": response.data[0] if response.data else {},
            "message": "Profile updated successfully"
        }
    except Exception as e:
        logger.error(f"Failed to update profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update profile")

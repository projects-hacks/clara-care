"""
Authentication & Authorization Dependency
Handles verifying JWT tokens from Supabase Auth and enforcing access control.
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)

# Singleton for the Auth-scoped Supabase client (respects RLS)
_auth_client: Optional[Client] = None

def get_auth_client() -> Client:
    """
    Lazily initialize a Supabase client using the ANON key.
    This client is used for user-facing auth operations and respects RLS.
    """
    global _auth_client
    if _auth_client is None:
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not anon_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY are required for Auth")
        _auth_client = create_client(url, anon_key)
    return _auth_client


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Any:
    """
    FastAPI Dependency: Extract and verify the Supabase JWT.
    Returns the authenticated user object.
    Raises 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        client = get_auth_client()
        # get_user verifies the JWT against Supabase Auth
        user_response = client.auth.get_user(token)
        if not user_response.user:
            raise ValueError("No user found in token")
        return user_response.user
    except Exception as e:
        logger.warning(f"Auth verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Any]:
    """
    FastAPI Dependency: Same as get_current_user, but returns None 
    instead of raising 401 if unauthenticated.
    """
    if credentials is None:
        return None
        
    try:
        client = get_auth_client()
        user_response = client.auth.get_user(credentials.credentials)
        return user_response.user
    except Exception:
        return None


async def verify_patient_access(store: Any, user_id: str, patient_id: str) -> None:
    """
    Helper to verify if a user has access to a specific patient.
    Users have access if they created the patient OR if they are an invited family contact.
    Raises 403 or 404 if access is denied.
    """
    patient = await store.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    # Check if user is the creator
    if patient.get("created_by") == user_id:
        return
        
    # Check if user is an authorized family contact
    # We need a method in DataStore to fetch contacts for a patient
    if hasattr(store, "get_family_contacts"):
        contacts = await store.get_family_contacts(patient_id)
        if any(c.get("user_id") == user_id for c in contacts):
            return
            
    # If neither, deny access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="You do not have access to this patient."
    )


from fastapi import Request

async def get_verified_patient_id(
    patient_id: str,
    request: Request,
    user: Any = Depends(get_current_user)
) -> str:
    """
    FastAPI dependency to verify user access to a patient.
    Can be used in any route that has patient_id as a path parameter.
    Returns the patient_id if access is granted.
    """
    from app.dependencies import get_data_store
    store = get_data_store(request)
    await verify_patient_access(store, user.id, patient_id)
    return patient_id

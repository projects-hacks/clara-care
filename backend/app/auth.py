"""
Authentication & Authorization Dependency
Handles verifying JWT tokens from Supabase Auth and enforcing access control.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
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
        auth_service = request.app.state.auth_service
        # get_user verifies the JWT against Supabase Auth
        user_response = auth_service.auth_client.auth.get_user(token)
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
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Any]:
    """
    FastAPI Dependency: Same as get_current_user, but returns None 
    instead of raising 401 if unauthenticated.
    """
    if credentials is None:
        return None
        
    try:
        auth_service = request.app.state.auth_service
        user_response = auth_service.auth_client.auth.get_user(credentials.credentials)
        return user_response.user
    except Exception:
        return None

def verify_patient_access(patient_repo, contact_repo, user_id: str, patient_id: str) -> None:
    """
    Verify if a user has access to a specific patient.
    Users have access if they created the patient OR if they are an invited family contact.
    Raises 403 or 404 if access is denied.
    """
    patient = patient_repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    if patient.get("created_by") == user_id:
        return
        
    contacts = contact_repo.get_for_patient(patient_id)
    if any(c.get("user_id") == user_id for c in contacts):
        return
            
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="You do not have access to this patient."
    )

async def get_verified_patient_id(
    patient_id: str,
    request: Request,
    user: Any = Depends(get_current_user)
) -> str:
    """
    FastAPI dependency to verify user access to a patient.
    Returns the patient_id if access is granted.
    """
    patient_repo = request.app.state.patient_repo
    contact_repo = request.app.state.contact_repo
    verify_patient_access(patient_repo, contact_repo, user.id, patient_id)
    return patient_id

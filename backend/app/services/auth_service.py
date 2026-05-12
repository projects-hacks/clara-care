import logging
from typing import Dict, Any
from fastapi import HTTPException
from supabase import Client

logger = logging.getLogger(__name__)

class AuthService:
    """
    Handles user authentication via Supabase GoTrue.
    This is the ONLY service that uses the Anon client (which respects RLS for auth operations).
    """
    def __init__(self, auth_client: Client, profile_repo):
        self.auth_client = auth_client
        self.profile_repo = profile_repo

    def sign_up(self, email: str, password: str, display_name: str, phone: str = None) -> Dict[str, Any]:
        try:
            response = self.auth_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "display_name": display_name,
                        "phone": phone
                    }
                }
            })
            
            if not response.user:
                raise HTTPException(status_code=400, detail="Signup failed")
                
            return {
                "success": True,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "display_name": display_name
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                }
            }
        except Exception as e:
            logger.error(f"Sign up failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        try:
            response = self.auth_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.session:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
            return {
                "success": True,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                }
            }
        except Exception as e:
            logger.error(f"Sign in failed: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        try:
            response = self.auth_client.auth.refresh_session(refresh_token)
            
            if not response.session:
                raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
                
            return {
                "success": True,
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                }
            }
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))

    def get_profile(self, user_id: str, email: str) -> Dict[str, Any]:
        profile = self.profile_repo.get_by_id(user_id) or {}
        return {
            "id": user_id,
            "email": email,
            "display_name": profile.get("display_name"),
            "phone": profile.get("phone"),
            "onboarding_completed": profile.get("onboarding_completed", False)
        }

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        if not updates:
            return {"success": True, "message": "No changes requested"}
            
        updated_profile = self.profile_repo.update(user_id, updates)
        return {
            "success": True,
            "profile": updated_profile,
            "message": "Profile updated successfully"
        }

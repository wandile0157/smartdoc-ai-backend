"""
Authentication Middleware
Handles JWT token verification from Supabase
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import httpx
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Security scheme for Bearer token
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def verify_token_with_supabase(token: str) -> dict:
    """
    Verify JWT token with Supabase.
    
    Args:
        token: JWT access token
        
    Returns:
        User data dict
        
    Raises:
        HTTPException: If token is invalid
    """
    if not settings.SUPABASE_URL:
        raise HTTPException(
            status_code=500,
            detail="Supabase is not configured"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_KEY
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "user_metadata": user_data.get("user_metadata", {}),
                    "created_at": user_data.get("created_at")
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    except httpx.RequestError as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not verify token: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Get current authenticated user (REQUIRED).
    Use this for protected endpoints.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        User info dict with id, email, etc.
        
    Raises:
        HTTPException: If not authenticated or token invalid
    """
    token = credentials.credentials
    return await verify_token_with_supabase(token)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(optional_security)
) -> Optional[dict]:
    """
    Get current user if authenticated, None otherwise (OPTIONAL).
    Use this for endpoints that work with or without auth.
    
    Args:
        credentials: Optional bearer token
        
    Returns:
        User info dict if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await verify_token_with_supabase(credentials.credentials)
    except HTTPException:
        return None


def is_auth_enabled() -> bool:
    """Check if authentication is properly configured"""
    return bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)
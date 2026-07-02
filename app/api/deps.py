"""
API dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import auth_service
from app.database.db import db_service
import structlog

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    payload = auth_service.decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await db_service.get_user_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    user.pop("password_hash", None)
    return user


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    try:
        payload = auth_service.decode_token(credentials.credentials)
        if not payload:
            return None
        user = await db_service.get_user_by_id(payload.get("sub"))
        if user:
            user.pop("password_hash", None)
        return user
    except Exception:
        return None

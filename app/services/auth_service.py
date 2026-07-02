"""
Authentication service
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.database.db import db_service
import structlog

logger = structlog.get_logger()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        except JWTError:
            return None
    
    async def authenticate_user(self, email: str, password: str):
        user = await db_service.get_user_by_email(email)
        if not user or not self.verify_password(password, user.get("password_hash", "")):
            return None
        return user
    
    async def register_user(self, email: str, password: str, full_name: str):
        existing = await db_service.get_user_by_email(email)
        if existing:
            raise ValueError("User already exists")
        
        user_data = {
            "email": email,
            "password_hash": self.get_password_hash(password),
            "full_name": full_name,
            "is_active": True
        }
        user = await db_service.create_user(user_data)
        user.pop("password_hash", None)
        return user


auth_service = AuthService()

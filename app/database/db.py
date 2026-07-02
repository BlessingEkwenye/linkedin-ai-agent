"""
Supabase database service using direct HTTP API
"""
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
import structlog
import uuid
from datetime import datetime

logger = structlog.get_logger()


class DatabaseService:
    def __init__(self):
        self.base_url = settings.supabase_url
        self.headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def _request(self, method: str, table: str, data: Any = None, query: str = ""):
        url = f"{self.base_url}/rest/v1/{table}"
        if query:
            url += f"?{query}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                resp = await client.get(url, headers=self.headers)
            elif method == "POST":
                resp = await client.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                resp = await client.patch(url, headers=self.headers, json=data)
            elif method == "DELETE":
                resp = await client.delete(url, headers=self.headers)
            
            resp.raise_for_status()
            return resp.json() if resp.text else []
    
    async def create_user(self, user_data: Dict[str, Any]):
        user_data["id"] = str(uuid.uuid4())
        user_data["created_at"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = datetime.utcnow().isoformat()
        result = await self._request("POST", "users", user_data)
        return result[0] if result else user_data
    
    async def get_user_by_email(self, email: str):
        result = await self._request("GET", "users", query=f"email=eq.{email}")
        return result[0] if result else None
    
    async def get_user_by_id(self, user_id: str):
        result = await self._request("GET", "users", query=f"id=eq.{user_id}")
        return result[0] if result else None
    
    async def save_post(self, post_data: Dict[str, Any], user_id: Optional[str] = None):
        post_data["id"] = str(uuid.uuid4())
        post_data["created_at"] = datetime.utcnow().isoformat()
        if user_id:
            post_data["user_id"] = user_id
        result = await self._request("POST", "posts", post_data)
        return result[0] if result else post_data
    
    async def get_post_by_id(self, post_id: str):
        result = await self._request("GET", "posts", query=f"id=eq.{post_id}")
        return result[0] if result else None
    
    async def save_calendar(self, calendar_data: Dict[str, Any], user_id: Optional[str] = None):
        calendar_data["id"] = str(uuid.uuid4())
        calendar_data["created_at"] = datetime.utcnow().isoformat()
        if user_id:
            calendar_data["user_id"] = user_id
        result = await self._request("POST", "calendars", calendar_data)
        return result[0] if result else calendar_data
    
    async def save_notion_sync(self, sync_data: Dict[str, Any]):
        sync_data["id"] = str(uuid.uuid4())
        sync_data["synced_at"] = datetime.utcnow().isoformat()
        result = await self._request("POST", "notion_syncs", sync_data)
        return result[0] if result else sync_data


db_service = DatabaseService()

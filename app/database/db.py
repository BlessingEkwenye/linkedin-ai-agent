"""
Supabase database service
"""
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.config import settings
import structlog
import uuid
from datetime import datetime

logger = structlog.get_logger()


class DatabaseService:
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize()
    
    def _initialize(self):
        try:
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("db_initialized")
        except Exception as e:
            logger.error("db_init_failed", error=str(e))
            raise
    
    async def create_user(self, user_data: Dict[str, Any]):
        user_data["id"] = str(uuid.uuid4())
        user_data["created_at"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = datetime.utcnow().isoformat()
        resp = self.client.table("users").insert(user_data).execute()
        return resp.data[0] if resp.data else user_data
    
    async def get_user_by_email(self, email: str):
        resp = self.client.table("users").select("*").eq("email", email).execute()
        return resp.data[0] if resp.data else None
    
    async def get_user_by_id(self, user_id: str):
        resp = self.client.table("users").select("*").eq("id", user_id).execute()
        return resp.data[0] if resp.data else None
    
    async def save_post(self, post_data: Dict[str, Any], user_id: Optional[str] = None):
        post_data["id"] = str(uuid.uuid4())
        post_data["created_at"] = datetime.utcnow().isoformat()
        if user_id:
            post_data["user_id"] = user_id
        resp = self.client.table("posts").insert(post_data).execute()
        return resp.data[0] if resp.data else post_data
    
    async def get_post_by_id(self, post_id: str):
        resp = self.client.table("posts").select("*").eq("id", post_id).execute()
        return resp.data[0] if resp.data else None
    
    async def save_calendar(self, calendar_data: Dict[str, Any], user_id: Optional[str] = None):
        calendar_data["id"] = str(uuid.uuid4())
        calendar_data["created_at"] = datetime.utcnow().isoformat()
        if user_id:
            calendar_data["user_id"] = user_id
        resp = self.client.table("calendars").insert(calendar_data).execute()
        return resp.data[0] if resp.data else calendar_data
    
    async def save_notion_sync(self, sync_data: Dict[str, Any]):
        sync_data["id"] = str(uuid.uuid4())
        sync_data["synced_at"] = datetime.utcnow().isoformat()
        resp = self.client.table("notion_syncs").insert(sync_data).execute()
        return resp.data[0] if resp.data else sync_data


db_service = DatabaseService()

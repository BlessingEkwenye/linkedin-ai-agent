"""
Supabase database service for persistent storage.
Handles all database operations with async support.
"""
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.config import settings
import structlog
import uuid
from datetime import datetime

logger = structlog.get_logger()


class DatabaseService:
    """Service for database operations using Supabase."""

    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize()

    def _initialize(self):
        """Initialize Supabase client."""
        try:
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("supabase_client_initialized")
        except Exception as e:
            logger.error("supabase_init_failed", error=str(e))
            raise

    # ==================== USER OPERATIONS ====================

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in the database."""
        try:
            user_data["id"] = str(uuid.uuid4())
            user_data["created_at"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = datetime.utcnow().isoformat()

            response = self.client.table("users").insert(user_data).execute()
            logger.info("user_created", user_id=user_data["id"])
            return response.data[0] if response.data else user_data
        except Exception as e:
            logger.error("create_user_failed", error=str(e))
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error("get_user_by_email_failed", error=str(e))
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error("get_user_by_id_failed", error=str(e))
            return None

    # ==================== POST OPERATIONS ====================

    async def save_post(self, post_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save a generated post to the database."""
        try:
            post_data["id"] = str(uuid.uuid4())
            post_data["created_at"] = datetime.utcnow().isoformat()
            post_data["updated_at"] = datetime.utcnow().isoformat()
            if user_id:
                post_data["user_id"] = user_id

            response = self.client.table("posts").insert(post_data).execute()
            logger.info("post_saved", post_id=post_data["id"])
            return response.data[0] if response.data else post_data
        except Exception as e:
            logger.error("save_post_failed", error=str(e))
            raise

    async def get_posts(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get posts with optional user filter."""
        try:
            query = self.client.table("posts").select("*").order("created_at", desc=True).limit(limit)
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error("get_posts_failed", error=str(e))
            return []

    async def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a post by ID."""
        try:
            response = self.client.table("posts").select("*").eq("id", post_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error("get_post_by_id_failed", error=str(e))
            return None

    async def update_post(self, post_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a post."""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            response = self.client.table("posts").update(updates).eq("id", post_id).execute()
            logger.info("post_updated", post_id=post_id)
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error("update_post_failed", error=str(e))
            return None

    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        try:
            self.client.table("posts").delete().eq("id", post_id).execute()
            logger.info("post_deleted", post_id=post_id)
            return True
        except Exception as e:
            logger.error("delete_post_failed", error=str(e))
            return False

    # ==================== CALENDAR OPERATIONS ====================

    async def save_calendar(self, calendar_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save a content calendar."""
        try:
            calendar_data["id"] = str(uuid.uuid4())
            calendar_data["created_at"] = datetime.utcnow().isoformat()
            calendar_data["updated_at"] = datetime.utcnow().isoformat()
            if user_id:
                calendar_data["user_id"] = user_id

            response = self.client.table("calendars").insert(calendar_data).execute()
            logger.info("calendar_saved", calendar_id=calendar_data["id"])
            return response.data[0] if response.data else calendar_data
        except Exception as e:
            logger.error("save_calendar_failed", error=str(e))
            raise

    async def get_calendars(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get calendars."""
        try:
            query = self.client.table("calendars").select("*").order("created_at", desc=True)
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error("get_calendars_failed", error=str(e))
            return []

    # ==================== BRAND VOICE OPERATIONS ====================

    async def save_brand_voice(self, voice_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save a brand voice profile."""
        try:
            voice_data["id"] = str(uuid.uuid4())
            voice_data["created_at"] = datetime.utcnow().isoformat()
            voice_data["updated_at"] = datetime.utcnow().isoformat()
            if user_id:
                voice_data["user_id"] = user_id

            response = self.client.table("brand_voices").insert(voice_data).execute()
            logger.info("brand_voice_saved", voice_id=voice_data["id"])
            return response.data[0] if response.data else voice_data
        except Exception as e:
            logger.error("save_brand_voice_failed", error=str(e))
            raise

    async def get_brand_voices(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get brand voice profiles."""
        try:
            query = self.client.table("brand_voices").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error("get_brand_voices_failed", error=str(e))
            return []

    # ==================== RESEARCH OPERATIONS ====================

    async def save_research(self, research_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save research results."""
        try:
            research_data["id"] = str(uuid.uuid4())
            research_data["created_at"] = datetime.utcnow().isoformat()
            if user_id:
                research_data["user_id"] = user_id

            response = self.client.table("research").insert(research_data).execute()
            logger.info("research_saved", research_id=research_data["id"])
            return response.data[0] if response.data else research_data
        except Exception as e:
            logger.error("save_research_failed", error=str(e))
            raise

    # ==================== NOTION SYNC OPERATIONS ====================

    async def save_notion_sync(self, sync_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save Notion sync record."""
        try:
            sync_data["id"] = str(uuid.uuid4())
            sync_data["synced_at"] = datetime.utcnow().isoformat()

            response = self.client.table("notion_syncs").insert(sync_data).execute()
            logger.info("notion_sync_saved", sync_id=sync_data["id"])
            return response.data[0] if response.data else sync_data
        except Exception as e:
            logger.error("save_notion_sync_failed", error=str(e))
            raise


# Singleton instance
db_service = DatabaseService()

"""
Notion integration service using direct HTTP API
"""
from typing import Optional, Dict, Any
import httpx
from app.config import settings
import structlog

logger = structlog.get_logger()


class NotionService:
    def __init__(self):
        self.api_key = settings.notion_api_key
        self.database_id = settings.notion_database_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        } if self.api_key and self.api_key.startswith("secret_") else {}
    
    def is_configured(self) -> bool:
        return bool(self.api_key and self.database_id)
    
    async def save_post(self, post_data: Dict[str, Any], database_id: Optional[str] = None):
        if not self.is_configured():
            return {"success": False, "message": "Notion not configured"}
        
        db_id = database_id or self.database_id
        content = post_data.get("content", {})
        hook = content.get("hook", "")
        body = content.get("body", "")
        cta = content.get("cta", "")
        hashtags = content.get("hashtags", [])
        title = (hook or post_data.get("topic", "Post"))[:100]
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.notion.com/v1/pages",
                    headers=self.headers,
                    json={
                        "parent": {"database_id": db_id},
                        "properties": {
                            "Name": {"title": [{"text": {"content": title}}]},
                            "Topic": {"rich_text": [{"text": {"content": post_data.get("topic", "")}}]},
                            "Brand Voice": {"select": {"name": post_data.get("brand_voice", "professional")}},
                            "Status": {"select": {"name": "Draft"}}
                        },
                        "children": [
                            {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Hook"}}]}},
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": hook or "No hook"}}]}},
                            {"object": "block", "type": "divider", "divider": {}},
                            {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Body"}}]}},
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": body or "No body"}}]}},
                            {"object": "block", "type": "divider", "divider": {}},
                            {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "CTA"}}]}},
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": cta or "No CTA"}}]}},
                            {"object": "block", "type": "divider", "divider": {}},
                            {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Hashtags"}}]}},
                            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": " ".join([f"#{h}" for h in hashtags]) or "None"}}]}}
                        ]
                    }
                )
                resp.raise_for_status()
                page = resp.json()
                return {
                    "success": True,
                    "notion_page_id": page["id"],
                    "notion_url": f"https://notion.so/{page['id'].replace('-', '')}",
                    "message": "Saved to Notion"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed: {str(e)}"}
    
    async def test_connection(self):
        if not self.is_configured():
            return {"success": False, "message": "Notion not configured"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://api.notion.com/v1/users/me", headers=self.headers)
                resp.raise_for_status()
                me = resp.json()
                return {"success": True, "message": f"Connected as {me.get('name', 'Unknown')}"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}


notion_service = NotionService()

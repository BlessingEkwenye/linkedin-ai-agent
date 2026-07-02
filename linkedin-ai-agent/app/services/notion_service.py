"""
Notion integration service for saving LinkedIn content to Notion.
"""
from typing import Optional, Dict, Any, List
from notion_database import NotionClient, PropertyValue, BlockContent, RichText, Icon
from app.config import settings
import structlog

logger = structlog.get_logger()


class NotionService:
    """Service for Notion integration."""

    def __init__(self):
        self.client: Optional[NotionClient] = None
        self.database_id: Optional[str] = None
        self._initialize()

    def _initialize(self):
        """Initialize Notion client if credentials are available."""
        if settings.notion_api_key and settings.notion_api_key.startswith("secret_"):
            try:
                self.client = NotionClient(settings.notion_api_key)
                self.database_id = settings.notion_database_id
                logger.info("notion_client_initialized")
            except Exception as e:
                logger.warning("notion_init_failed", error=str(e))
        else:
            logger.info("notion_not_configured")

    def is_configured(self) -> bool:
        """Check if Notion is properly configured."""
        return self.client is not None and self.database_id is not None

    async def save_post(
        self,
        post_data: Dict[str, Any],
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save a LinkedIn post to Notion database."""
        if not self.is_configured():
            return {
                "success": False,
                "message": "Notion integration not configured. Please set NOTION_API_KEY and NOTION_DATABASE_ID."
            }

        db_id = database_id or self.database_id

        try:
            content = post_data.get("content", {})
            hook = content.get("hook", "")
            body = content.get("body", "")
            cta = content.get("cta", "")
            hashtags = content.get("hashtags", [])

            # Build the page title from hook or topic
            title = hook if hook else post_data.get("topic", "LinkedIn Post")
            if len(title) > 100:
                title = title[:97] + "..."

            # Create the page in Notion database
            page = self.client.pages.create(
                parent={"database_id": db_id},
                properties={
                    "Name": PropertyValue.title(title),
                    "Topic": PropertyValue.rich_text(post_data.get("topic", "")),
                    "Brand Voice": PropertyValue.select(post_data.get("brand_voice", "professional")),
                    "Tone": PropertyValue.select(post_data.get("tone", "conversational")),
                    "Status": PropertyValue.select("Draft"),
                    "Character Count": PropertyValue.number(content.get("character_count", 0)),
                    "Word Count": PropertyValue.number(content.get("word_count", 0)),
                    "Confidence Score": PropertyValue.number(
                        post_data.get("confidence_score", 0.8)
                    ),
                    "AI Model": PropertyValue.rich_text(post_data.get("ai_model", "gpt-4o")),
                    "Hashtags": PropertyValue.rich_text(
                        " ".join([f"#{h}" for h in hashtags]) if hashtags else ""
                    ),
                },
                icon=Icon.emoji("📝"),
                children=[
                    BlockContent.heading_1("Hook"),
                    BlockContent.paragraph(hook or "No hook generated"),
                    BlockContent.divider(),
                    BlockContent.heading_1("Body"),
                    *self._split_into_paragraphs(body),
                    BlockContent.divider(),
                    BlockContent.heading_1("Call to Action"),
                    BlockContent.paragraph(cta or "No CTA generated"),
                    BlockContent.divider(),
                    BlockContent.heading_1("Hashtags"),
                    BlockContent.paragraph(
                        " ".join([f"#{h}" for h in hashtags]) if hashtags else "No hashtags"
                    ),
                    BlockContent.divider(),
                    BlockContent.heading_1("Metadata"),
                    BlockContent.bulleted_list_item(f"Topic: {post_data.get('topic', 'N/A')}"),
                    BlockContent.bulleted_list_item(f"Brand Voice: {post_data.get('brand_voice', 'N/A')}"),
                    BlockContent.bulleted_list_item(f"Tone: {post_data.get('tone', 'N/A')}"),
                    BlockContent.bulleted_list_item(f"AI Model: {post_data.get('ai_model', 'N/A')}"),
                    BlockContent.bulleted_list_item(f"Confidence Score: {post_data.get('confidence_score', 0)}"),
                ]
            )

            logger.info("post_saved_to_notion", page_id=page["id"])

            return {
                "success": True,
                "notion_page_id": page["id"],
                "notion_url": f"https://notion.so/{page['id'].replace('-', '')}",
                "message": "Post successfully saved to Notion"
            }

        except Exception as e:
            logger.error("notion_save_failed", error=str(e))
            return {
                "success": False,
                "message": f"Failed to save to Notion: {str(e)}"
            }

    async def save_calendar(
        self,
        calendar_data: Dict[str, Any],
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save a content calendar to Notion."""
        if not self.is_configured():
            return {
                "success": False,
                "message": "Notion integration not configured"
            }

        db_id = database_id or self.database_id

        try:
            calendar_name = calendar_data.get("name", "LinkedIn Content Calendar")
            posts = calendar_data.get("posts", [])

            # Create a parent page for the calendar
            calendar_page = self.client.pages.create(
                parent={"database_id": db_id},
                properties={
                    "Name": PropertyValue.title(calendar_name),
                    "Topic": PropertyValue.rich_text("Content Calendar"),
                    "Brand Voice": PropertyValue.select(calendar_data.get("brand_voice", "professional")),
                    "Status": PropertyValue.select("Planning"),
                    "Character Count": PropertyValue.number(0),
                    "Word Count": PropertyValue.number(len(posts)),
                },
                icon=Icon.emoji("📅"),
                children=[
                    BlockContent.heading_1(f"Content Calendar: {calendar_name}"),
                    BlockContent.paragraph(
                        f"Total posts: {len(posts)} | Duration: {calendar_data.get('duration_weeks', 4)} weeks"
                    ),
                    BlockContent.divider(),
                ]
            )

            # Add each post as a section
            for post in posts:
                self.client.blocks.append_children(
                    calendar_page["id"],
                    children=[
                        BlockContent.heading_2(post.get("topic", "Untitled Post")),
                        BlockContent.paragraph(f"📅 {post.get('date', 'TBD')} | Type: {post.get('content_type', 'text')}"),
                        BlockContent.paragraph(f"🎯 Suggested Hook: {post.get('suggested_hook', 'N/A')}"),
                        BlockContent.heading_3("Key Points"),
                        *[BlockContent.bulleted_list_item(kp) for kp in post.get("key_points", [])],
                        BlockContent.heading_3("Hashtags"),
                        BlockContent.paragraph(" ".join([f"#{h}" for h in post.get("suggested_hashtags", [])])),
                        BlockContent.divider(),
                    ]
                )

            logger.info("calendar_saved_to_notion", page_id=calendar_page["id"])

            return {
                "success": True,
                "notion_page_id": calendar_page["id"],
                "notion_url": f"https://notion.so/{calendar_page['id'].replace('-', '')}",
                "message": f"Calendar with {len(posts)} posts saved to Notion"
            }

        except Exception as e:
            logger.error("notion_calendar_save_failed", error=str(e))
            return {
                "success": False,
                "message": f"Failed to save calendar to Notion: {str(e)}"
            }

    def _split_into_paragraphs(self, text: str) -> List[Any]:
        """Split text into Notion paragraph blocks."""
        if not text:
            return [BlockContent.paragraph("No content")]

        paragraphs = text.split("\n\n")
        blocks = []
        for para in paragraphs:
            para = para.strip()
            if para:
                # Check if it's a heading (starts with # or ## or ###)
                if para.startswith("### "):
                    blocks.append(BlockContent.heading_3(para[4:]))
                elif para.startswith("## "):
                    blocks.append(BlockContent.heading_2(para[3:]))
                elif para.startswith("# "):
                    blocks.append(BlockContent.heading_1(para[2:]))
                else:
                    blocks.append(BlockContent.paragraph(para))
        return blocks if blocks else [BlockContent.paragraph(text)]

    async def test_connection(self) -> Dict[str, Any]:
        """Test Notion connection."""
        if not self.is_configured():
            return {
                "success": False,
                "message": "Notion not configured"
            }

        try:
            me = self.client.users.me()
            return {
                "success": True,
                "message": f"Connected as {me.get('name', 'Unknown')}",
                "bot_id": me.get("id")
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }


# Singleton instance
notion_service = NotionService()

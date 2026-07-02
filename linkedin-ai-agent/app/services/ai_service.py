"""
OpenAI Service for AI-powered content generation.
Handles all LLM interactions with retry logic and error handling.
"""
import json
import asyncio
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings
import structlog

logger = structlog.get_logger()


class AIService:
    """Service for AI-powered content operations."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_retries = 3
        self.retry_delay = 1.0

    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> str:
        """Call OpenAI API with retry logic."""
        for attempt in range(self.max_retries):
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }

                if response_format:
                    kwargs["response_format"] = response_format

                response = await self.client.chat.completions.create(**kwargs)

                content = response.choices[0].message.content
                logger.info(
                    "openai_call_success",
                    model=self.model,
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    attempt=attempt + 1
                )
                return content

            except Exception as e:
                logger.warning(
                    "openai_call_retry",
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error("openai_call_failed", error=str(e))
                    raise

    async def generate_post(
        self,
        topic: str,
        brand_voice: str,
        tone: str,
        content_type: str,
        target_audience: Optional[str],
        key_points: Optional[List[str]],
        include_hook: bool,
        include_cta: bool,
        include_hashtags: bool,
        max_length: int,
        research_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate a LinkedIn post using AI."""
        from app.prompts.prompts import (
            POST_GENERATION_SYSTEM_PROMPT,
            POST_GENERATION_USER_PROMPT,
            BRAND_VOICE_PROMPTS
        )

        brand_voice_prompt = BRAND_VOICE_PROMPTS.get(brand_voice, BRAND_VOICE_PROMPTS["professional"])

        system_prompt = POST_GENERATION_SYSTEM_PROMPT + "\n\n" + brand_voice_prompt

        research_ctx = f"Research context:\n{research_context}" if research_context else ""
        key_pts = "\n".join(f"- {kp}" for kp in key_points) if key_points else "None specified"

        user_prompt = POST_GENERATION_USER_PROMPT.format(
            topic=topic,
            brand_voice=brand_voice,
            tone=tone,
            content_type=content_type,
            target_audience=target_audience or "General professionals on LinkedIn",
            max_length=max_length,
            research_context=research_ctx,
            key_points=key_pts,
            include_hook="Yes" if include_hook else "No",
            include_cta="Yes" if include_cta else "No",
            include_hashtags="Yes" if include_hashtags else "No"
        )

        response = await self._call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.75,
            max_tokens=2500,
            response_format={"type": "json_object"}
        )

        return json.loads(response)

    async def research_topic(
        self,
        topic: str,
        depth: str,
        sources: List[str]
    ) -> Dict[str, Any]:
        """Research a topic using AI."""
        from app.prompts.prompts import RESEARCH_TOPIC_PROMPT

        user_prompt = RESEARCH_TOPIC_PROMPT.format(
            topic=topic,
            depth=depth,
            sources=", ".join(sources)
        )

        response = await self._call_openai(
            system_prompt="You are an expert research analyst. Return only valid JSON.",
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )

        return json.loads(response)

    async def generate_hooks(
        self,
        topic: str,
        brand_voice: str,
        count: int,
        hook_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate hook suggestions."""
        from app.prompts.prompts import HOOK_GENERATION_PROMPT, BRAND_VOICE_PROMPTS

        brand_voice_prompt = BRAND_VOICE_PROMPTS.get(brand_voice, BRAND_VOICE_PROMPTS["professional"])

        user_prompt = HOOK_GENERATION_PROMPT.format(
            count=count,
            topic=topic,
            brand_voice=brand_voice,
            hook_types=", ".join(hook_types)
        )

        response = await self._call_openai(
            system_prompt=f"You are a LinkedIn hook specialist. {brand_voice_prompt}",
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        result = json.loads(response)
        return result.get("suggestions", result.get("hooks", []))

    async def generate_ctas(
        self,
        post_topic: str,
        goal: str,
        brand_voice: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate CTA suggestions."""
        from app.prompts.prompts import CTA_GENERATION_PROMPT, BRAND_VOICE_PROMPTS

        brand_voice_prompt = BRAND_VOICE_PROMPTS.get(brand_voice, BRAND_VOICE_PROMPTS["professional"])

        user_prompt = CTA_GENERATION_PROMPT.format(
            count=count,
            post_topic=post_topic,
            goal=goal,
            brand_voice=brand_voice
        )

        response = await self._call_openai(
            system_prompt=f"You are a conversion copywriter. {brand_voice_prompt}",
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        result = json.loads(response)
        return result.get("suggestions", result.get("ctas", []))

    async def generate_hashtags(
        self,
        topic: str,
        niche: Optional[str],
        count: int,
        include_trending: bool
    ) -> List[Dict[str, Any]]:
        """Generate hashtag suggestions."""
        from app.prompts.prompts import HASHTAG_GENERATION_PROMPT

        user_prompt = HASHTAG_GENERATION_PROMPT.format(
            count=count,
            topic=topic,
            niche=niche or "General professional",
            include_trending="Yes" if include_trending else "No"
        )

        response = await self._call_openai(
            system_prompt="You are a LinkedIn hashtag strategist. Return only valid JSON.",
            user_prompt=user_prompt,
            temperature=0.6,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        result = json.loads(response)
        return result.get("suggestions", result.get("hashtags", []))

    async def rewrite_post(
        self,
        original_post: str,
        improvement_goal: str,
        brand_voice: Optional[str],
        preserve_length: bool
    ) -> Dict[str, Any]:
        """Rewrite and improve a post."""
        from app.prompts.prompts import POST_REWRITE_PROMPT, BRAND_VOICE_PROMPTS

        brand_voice_prompt = ""
        if brand_voice:
            brand_voice_prompt = BRAND_VOICE_PROMPTS.get(brand_voice, "")

        user_prompt = POST_REWRITE_PROMPT.format(
            original_post=original_post,
            improvement_goal=improvement_goal,
            brand_voice=brand_voice or "Maintain original voice",
            preserve_length="Yes" if preserve_length else "No"
        )

        response = await self._call_openai(
            system_prompt=f"You are a LinkedIn content editor. {brand_voice_prompt}",
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )

        return json.loads(response)

    async def generate_calendar(
        self,
        topics: List[str],
        brand_voice: str,
        start_date: str,
        duration_weeks: int,
        posts_per_week: int,
        content_mix: Optional[Dict[str, int]]
    ) -> List[Dict[str, Any]]:
        """Generate a content calendar."""
        from app.prompts.prompts import CALENDAR_GENERATION_PROMPT, BRAND_VOICE_PROMPTS

        brand_voice_prompt = BRAND_VOICE_PROMPTS.get(brand_voice, BRAND_VOICE_PROMPTS["professional"])

        mix_str = ""
        if content_mix:
            mix_str = "\n".join(f"- {k}: {v}%" for k, v in content_mix.items())
        else:
            mix_str = "- Educational: 40%\n- Engaging/Storytelling: 30%\n- Promotional: 20%\n- Industry Commentary: 10%"

        user_prompt = CALENDAR_GENERATION_PROMPT.format(
            duration_weeks=duration_weeks,
            posts_per_week=posts_per_week,
            topics=", ".join(topics),
            brand_voice=brand_voice,
            start_date=start_date,
            content_mix=mix_str
        )

        response = await self._call_openai(
            system_prompt=f"You are a content calendar strategist. {brand_voice_prompt}",
            user_prompt=user_prompt,
            temperature=0.75,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        result = json.loads(response)
        return result.get("posts", result.get("calendar", []))

    async def deep_research(
        self,
        topic: str
    ) -> Dict[str, Any]:
        """Conduct deep research on a topic."""
        from app.prompts.prompts import RESEARCH_DEEP_DIVE_PROMPT

        user_prompt = RESEARCH_DEEP_DIVE_PROMPT.format(topic=topic)

        response = await self._call_openai(
            system_prompt="You are a senior research analyst. Return only valid JSON.",
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        return json.loads(response)


# Singleton instance
ai_service = AIService()

"""
OpenAI Service
"""
import json
import asyncio
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings
import structlog

logger = structlog.get_logger()


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_retries = 3
    
    async def _call(self, system: str, user: str, temp: float = 0.7, max_tokens: int = 2000):
        for attempt in range(self.max_retries):
            try:
                resp = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    temperature=temp,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                return json.loads(resp.choices[0].message.content)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise e
    
    async def generate_post(self, topic, brand_voice, tone, content_type, target_audience, key_points, include_hook, include_cta, include_hashtags, max_length, research_context):
        system = f"""You are an elite LinkedIn copywriter. Write in a {brand_voice} voice with a {tone} tone.
Rules: Strong hook first, short paragraphs, clear CTA, max {max_length} chars. Return JSON with hook, body, cta, hashtags, character_count, word_count."""
        
        user = f"""Topic: {topic}
Target: {target_audience or 'professionals'}
Key points: {key_points or 'None'}
Research: {research_context or 'None'}
Include hook: {include_hook}, CTA: {include_cta}, Hashtags: {include_hashtags}"""
        
        return await self._call(system, user, temp=0.75, max_tokens=2500)
    
    async def research_topic(self, topic, depth, sources):
        system = "You are a research analyst. Return JSON with summary, key_insights, trends, statistics, content_angles."
        user = f"Research '{topic}' at {depth} depth using sources: {', '.join(sources)}"
        return await self._call(system, user, temp=0.5, max_tokens=3000)
    
    async def generate_hooks(self, topic, brand_voice, count, hook_types):
        system = f"You are a LinkedIn hook specialist. Generate {count} hooks in {brand_voice} voice. Return JSON array of hooks with hook_text, hook_type, predicted_engagement, explanation."
        user = f"Topic: {topic}. Hook types: {', '.join(hook_types)}"
        result = await self._call(system, user, temp=0.8, max_tokens=2000)
        return result.get("suggestions", result.get("hooks", []))
    
    async def generate_ctas(self, post_topic, goal, brand_voice, count):
        system = f"You are a conversion copywriter. Generate {count} CTAs for {goal} goal in {brand_voice} voice. Return JSON array with cta_text, cta_type, goal_alignment."
        user = f"Post topic: {post_topic}. Goal: {goal}"
        result = await self._call(system, user, temp=0.7, max_tokens=1500)
        return result.get("suggestions", result.get("ctas", []))
    
    async def generate_hashtags(self, topic, niche, count, include_trending):
        system = f"You are a LinkedIn hashtag strategist. Generate {count} hashtags. Return JSON array with tag, relevance_score, estimated_reach, category."
        user = f"Topic: {topic}. Niche: {niche or 'general'}. Include trending: {include_trending}"
        result = await self._call(system, user, temp=0.6, max_tokens=1500)
        return result.get("suggestions", result.get("hashtags", []))
    
    async def rewrite_post(self, original_post, improvement_goal, brand_voice, preserve_length):
        system = f"You are a LinkedIn editor. Improve for {improvement_goal}. Voice: {brand_voice or 'original'}. Return JSON with rewritten_post, improvements_made, weaknesses."
        user = f"Original:\\n{original_post}\\nPreserve length: {preserve_length}"
        return await self._call(system, user, temp=0.7, max_tokens=3000)
    
    async def generate_calendar(self, topics, brand_voice, start_date, duration_weeks, posts_per_week, content_mix):
        total_posts = duration_weeks * posts_per_week
        system = f"You are a content calendar strategist. Create {total_posts} posts over {duration_weeks} weeks. Return JSON array of posts with date, topic, content_type, suggested_hook, key_points, suggested_hashtags."
        user = f"Topics: {', '.join(topics)}. Voice: {brand_voice}. Start: {start_date}. Mix: {content_mix or 'default'}"
        result = await self._call(system, user, temp=0.75, max_tokens=4000)
        return result.get("posts", result.get("calendar", []))


ai_service = AIService()

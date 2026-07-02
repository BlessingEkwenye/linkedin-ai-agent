"""
Pydantic models
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BrandVoice(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    CONTROVERSIAL = "controversial"
    HUMOROUS = "humorous"
    AUTHORITY = "authority"


class PostTone(str, Enum):
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    ENERGETIC = "energetic"
    CALM = "calm"
    PERSUASIVE = "persuasive"


class ContentType(str, Enum):
    TEXT = "text"
    CAROUSEL = "carousel"
    POLL = "poll"
    ARTICLE = "article"
    VIDEO = "video"
    SINGLE_IMAGE = "single_image"


class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime
    is_active: bool = True


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    depth: str = Field(default="medium", pattern="^(shallow|medium|deep)$")
    sources: List[str] = Field(default=["web", "news"])
    max_results: int = Field(default=5, ge=1, le=20)


class PostGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    tone: PostTone = PostTone.CONVERSATIONAL
    content_type: ContentType = ContentType.TEXT
    target_audience: Optional[str] = None
    key_points: Optional[List[str]] = None
    include_hook: bool = True
    include_cta: bool = True
    include_hashtags: bool = True
    max_length: int = Field(default=3000, ge=100, le=3000)
    research_context: Optional[str] = None


class HookSuggestionRequest(BaseModel):
    topic: str
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    count: int = Field(default=5, ge=1, le=10)
    hook_types: List[str] = Field(default=["question", "statistic", "story", "contrarian"])


class CTASuggestionRequest(BaseModel):
    post_topic: str
    goal: str = Field(..., pattern="^(engagement|traffic|leads|followers|comments|shares)$")
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    count: int = Field(default=3, ge=1, le=5)


class HashtagSuggestionRequest(BaseModel):
    topic: str
    niche: Optional[str] = None
    count: int = Field(default=10, ge=3, le=30)
    include_trending: bool = True


class PostRewriteRequest(BaseModel):
    original_post: str = Field(..., min_length=10)
    improvement_goal: str = Field(..., pattern="^(engagement|clarity|professionalism|storytelling|conciseness|hook_strength)$")
    brand_voice: Optional[BrandVoice] = None
    preserve_length: bool = True


class CalendarGenerateRequest(BaseModel):
    topics: List[str] = Field(..., min_length=1, max_length=20)
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    start_date: datetime
    duration_weeks: int = Field(default=4, ge=1, le=12)
    posts_per_week: int = Field(default=3, ge=1, le=7)
    content_mix: Optional[Dict[str, int]] = None
    include_research: bool = True


class NotionSaveRequest(BaseModel):
    post_id: str
    database_id: Optional[str] = None


class BrandVoiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    tone_adjectives: List[str] = Field(..., min_length=3, max_length=10)
    vocabulary_style: str
    sentence_structure: str
    emoji_usage: str = "minimal"
    example_posts: Optional[List[str]] = None

"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BrandVoice(str, Enum):
    """Supported brand voice styles."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    CONTROVERSIAL = "controversial"
    HUMOROUS = "humorous"
    AUTHORITY = "authority"


class PostTone(str, Enum):
    """Post tone options."""
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    ENERGETIC = "energetic"
    CALM = "calm"
    PERSUASIVE = "persuasive"


class ContentType(str, Enum):
    """Types of LinkedIn content."""
    TEXT = "text"
    CAROUSEL = "carousel"
    POLL = "poll"
    ARTICLE = "article"
    VIDEO = "video"
    SINGLE_IMAGE = "single_image"


# ==================== AUTH MODELS ====================

class UserCreate(BaseModel):
    """User registration request."""
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
    """User login request."""
    email: str
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User data response."""
    id: str
    email: str
    full_name: str
    created_at: datetime
    is_active: bool = True


# ==================== RESEARCH MODELS ====================

class ResearchRequest(BaseModel):
    """Topic research request."""
    topic: str = Field(..., min_length=3, max_length=500)
    depth: str = Field(default="medium", pattern="^(shallow|medium|deep)$")
    sources: List[str] = Field(default=["web", "news", "academic"])
    max_results: int = Field(default=5, ge=1, le=20)


class ResearchResult(BaseModel):
    """Research result item."""
    title: str
    source: str
    url: Optional[str] = None
    summary: str
    key_points: List[str]
    relevance_score: float = Field(..., ge=0, le=1)


class ResearchResponse(BaseModel):
    """Research response."""
    topic: str
    results: List[ResearchResult]
    generated_at: datetime
    total_sources: int


# ==================== POST GENERATION MODELS ====================

class PostGenerateRequest(BaseModel):
    """LinkedIn post generation request."""
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


class PostContent(BaseModel):
    """Generated post content."""
    hook: Optional[str] = None
    body: str
    cta: Optional[str] = None
    hashtags: Optional[List[str]] = None
    estimated_read_time: str
    character_count: int
    word_count: int


class PostGenerateResponse(BaseModel):
    """Post generation response."""
    id: str
    content: PostContent
    brand_voice: str
    tone: str
    topic: str
    generated_at: datetime
    ai_model: str
    confidence_score: float = Field(..., ge=0, le=1)


# ==================== POST REWRITE MODELS ====================

class PostRewriteRequest(BaseModel):
    """Post rewrite/improvement request."""
    original_post: str = Field(..., min_length=10)
    improvement_goal: str = Field(..., pattern="^(engagement|clarity|professionalism|storytelling|conciseness|hook_strength)$")
    brand_voice: Optional[BrandVoice] = None
    preserve_length: bool = True


class PostRewriteResponse(BaseModel):
    """Post rewrite response."""
    id: str
    original_post: str
    rewritten_post: str
    improvements_made: List[str]
    before_after_comparison: Dict[str, Any]
    generated_at: datetime


# ==================== HOOK/CTA/HASHTAG MODELS ====================

class HookSuggestionRequest(BaseModel):
    """Hook suggestion request."""
    topic: str
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    count: int = Field(default=5, ge=1, le=10)
    hook_types: List[str] = Field(default=["question", "statistic", "story", "contrarian", "how_to"])


class HookSuggestion(BaseModel):
    """Individual hook suggestion."""
    hook_text: str
    hook_type: str
    predicted_engagement: str  # low, medium, high
    explanation: str


class HookSuggestionResponse(BaseModel):
    """Hook suggestions response."""
    topic: str
    suggestions: List[HookSuggestion]
    generated_at: datetime


class CTASuggestionRequest(BaseModel):
    """CTA suggestion request."""
    post_topic: str
    goal: str = Field(..., pattern="^(engagement|traffic|leads|followers|comments|shares)$")
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    count: int = Field(default=3, ge=1, le=5)


class CTASuggestion(BaseModel):
    """Individual CTA suggestion."""
    cta_text: str
    cta_type: str
    goal_alignment: str


class CTASuggestionResponse(BaseModel):
    """CTA suggestions response."""
    post_topic: str
    suggestions: List[CTASuggestion]
    generated_at: datetime


class HashtagSuggestionRequest(BaseModel):
    """Hashtag suggestion request."""
    topic: str
    niche: Optional[str] = None
    count: int = Field(default=10, ge=3, le=30)
    include_trending: bool = True


class HashtagSuggestion(BaseModel):
    """Individual hashtag suggestion."""
    tag: str
    relevance_score: float = Field(..., ge=0, le=1)
    estimated_reach: str  # low, medium, high
    category: str  # niche, broad, trending, branded


class HashtagSuggestionResponse(BaseModel):
    """Hashtag suggestions response."""
    topic: str
    suggestions: List[HashtagSuggestion]
    generated_at: datetime


# ==================== CALENDAR MODELS ====================

class CalendarGenerateRequest(BaseModel):
    """Content calendar generation request."""
    topics: List[str] = Field(..., min_length=1, max_length=20)
    brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    start_date: datetime
    duration_weeks: int = Field(default=4, ge=1, le=12)
    posts_per_week: int = Field(default=3, ge=1, le=7)
    content_mix: Optional[Dict[str, int]] = None  # {"educational": 40, "promotional": 20, ...}
    include_research: bool = True


class CalendarPost(BaseModel):
    """Individual calendar post entry."""
    date: datetime
    topic: str
    content_type: ContentType
    brand_voice: BrandVoice
    suggested_hook: str
    key_points: List[str]
    suggested_hashtags: List[str]
    status: str = "draft"  # draft, scheduled, published


class CalendarResponse(BaseModel):
    """Content calendar response."""
    id: str
    name: str
    posts: List[CalendarPost]
    total_posts: int
    generated_at: datetime
    date_range: Dict[str, datetime]


# ==================== NOTION MODELS ====================

class NotionSaveRequest(BaseModel):
    """Save to Notion request."""
    post_id: str
    database_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class NotionSaveResponse(BaseModel):
    """Notion save response."""
    success: bool
    notion_page_id: Optional[str] = None
    notion_url: Optional[str] = None
    message: str


# ==================== BRAND VOICE MODELS ====================

class BrandVoiceProfile(BaseModel):
    """Brand voice profile."""
    id: str
    name: str
    description: str
    tone_adjectives: List[str]
    vocabulary_style: str
    sentence_structure: str
    emoji_usage: str = "minimal"
    example_posts: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class BrandVoiceCreate(BaseModel):
    """Create brand voice profile."""
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    tone_adjectives: List[str] = Field(..., min_length=3, max_length=10)
    vocabulary_style: str
    sentence_structure: str
    emoji_usage: str = "minimal"
    example_posts: Optional[List[str]] = None


# ==================== HEALTH MODELS ====================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
    timestamp: datetime
    services: Dict[str, str]

"""
OpenShelf MVP v1 — Pydantic Schemas
Request and response models for all API endpoints.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.models import UserRole, BookCondition, ListingStatus, NotificationType, ConversationStatus


# ============================================================
#  AUTH
# ============================================================

class UserRegister(BaseModel):
    email: str = Field(..., description="Must be a .edu email address")
    password: str = Field(..., min_length=6)
    first_name: str
    last_name: str
    role: UserRole = UserRole.student
    university_id: int


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    university_id: int
    is_verified: bool
    created_at: Optional[datetime] = None


class UserProfile(UserOut):
    """Extended user profile with aggregated stats."""
    average_rating: Optional[float] = None
    total_reviews: int = 0
    active_listings: int = 0


# ============================================================
#  UNIVERSITY
# ============================================================

class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    domain: str


# ============================================================
#  COURSE
# ============================================================

class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_code: str
    course_name: str
    professor: Optional[str] = None
    semester: str
    university_id: int


class CourseWithTextbooks(CourseOut):
    textbooks: List["TextbookOut"] = []


# ============================================================
#  TEXTBOOK
# ============================================================

class TextbookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    isbn: str
    title: str
    author: str
    edition: Optional[str] = None
    publisher: Optional[str] = None
    retail_price: Optional[float] = None
    image_url: Optional[str] = None


# ============================================================
#  LISTING
# ============================================================

class ListingCreate(BaseModel):
    textbook_id: int
    condition: BookCondition
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: List[str] = []


class ListingUpdate(BaseModel):
    condition: Optional[BookCondition] = None
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    status: Optional[ListingStatus] = None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    seller_id: int
    textbook_id: int
    condition: BookCondition
    price: float
    ai_recommended_price: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: List[str] = []
    status: ListingStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("image_urls", mode="before")
    @classmethod
    def coerce_image_urls(cls, v):
        return v if isinstance(v, list) else []


class ListingDetail(ListingOut):
    """Listing with nested seller and textbook info."""
    seller: Optional[UserOut] = None
    textbook: Optional[TextbookOut] = None


class ListingSearch(BaseModel):
    """Query parameters for listing search."""
    course_id: Optional[int] = None
    isbn: Optional[str] = None
    title: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[BookCondition] = None
    status: ListingStatus = ListingStatus.active


class AIPriceRequest(BaseModel):
    textbook_id: int
    condition: BookCondition


class AIPriceResponse(BaseModel):
    textbook_id: int
    condition: BookCondition
    retail_price: Optional[float] = None
    recommended_price: float
    savings_vs_retail: Optional[float] = None
    reasoning: str


# ============================================================
#  MATCHING
# ============================================================

class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    listing_id: int
    buyer_id: int
    match_score: float
    matched_at: Optional[datetime] = None


class MatchDetail(MatchOut):
    listing: Optional[ListingDetail] = None


class MatchGenerateResponse(BaseModel):
    user_id: int
    matches_generated: int
    matches: List[MatchDetail] = []


# ============================================================
#  MESSAGE / CONVERSATION
# ============================================================

class MessageCreate(BaseModel):
    """Legacy message-create payload for backward compatibility with v1 demo.

    Used by POST /messages/ — the server resolves (or creates) the
    conversation between the current user and `receiver_id` about
    `listing_id`, then appends a message to it.
    """
    receiver_id: int
    listing_id: int
    content: str
    is_agentic: bool = False


class ConversationMessageCreate(BaseModel):
    """Payload for appending a message to an existing conversation.

    Used by POST /conversations/{id}/messages — the conversation is inferred
    from the URL, so no receiver/listing fields are needed.
    """
    content: str
    is_agentic: bool = False


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    conversation_id: int
    sender_id: int
    content: str
    is_agentic: bool
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


class ConversationCreate(BaseModel):
    """Start a new conversation about a listing. Seller is inferred from the listing."""
    listing_id: int
    initial_message: Optional[str] = None
    is_agentic: bool = True


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    status: ConversationStatus
    created_at: Optional[datetime] = None


class ConversationDetail(ConversationOut):
    """Conversation enriched with participants, listing, and message thread."""
    buyer: Optional[UserOut] = None
    seller: Optional[UserOut] = None
    listing: Optional[ListingOut] = None
    messages: List[MessageOut] = []


class ConversationSummary(BaseModel):
    """Row in the inbox — latest activity for a conversation from the user's point of view."""
    conversation: ConversationOut
    other_user: UserOut
    listing: Optional[ListingOut] = None
    last_message: Optional[MessageOut] = None
    unread_count: int


# ============================================================
#  REVIEW
# ============================================================

class ReviewCreate(BaseModel):
    reviewed_user_id: int
    listing_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reviewer_id: int
    reviewed_user_id: int
    listing_id: int
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


class ReviewWithReviewer(ReviewOut):
    reviewer: Optional[UserOut] = None


# ============================================================
#  NOTIFICATION
# ============================================================

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    type: NotificationType
    content: str
    is_read: bool
    reference_id: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================
#  ENROLLMENT
# ============================================================

class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    course_id: int
    semester: str


class EnrollmentWithCourse(EnrollmentOut):
    course: Optional[CourseOut] = None


# ============================================================
#  CHATBOT
# ============================================================

class ChatTurn(BaseModel):
    """One turn in a chatbot conversation history."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[ChatTurn] = Field(default_factory=list)


class ChatSource(BaseModel):
    """A retrieved document cited in the chatbot's response."""
    kind: str = Field(..., description="listing, course, textbook, faq, pricing, comparison")
    title: str
    snippet: str
    reference_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[ChatSource] = Field(default_factory=list)
    model: str = Field(..., description="Model name, or 'template' for fallback")


# ============================================================
#  DASHBOARD / AGGREGATE
# ============================================================

class DashboardResponse(BaseModel):
    """What a buyer sees when they log in."""
    user: UserOut
    enrolled_courses: List[CourseWithTextbooks] = []
    recommended_listings: List[MatchDetail] = []
    notifications: List[NotificationOut] = []

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.models import ConditionEnum, ListingStatusEnum, RoleEnum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    role: RoleEnum


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleEnum

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ListingCreate(BaseModel):
    textbook_id: int
    condition: ConditionEnum
    price: float
    description: str | None = None


class ListingOut(BaseModel):
    id: int
    seller_id: int
    textbook_id: int
    condition: ConditionEnum
    price: float
    ai_recommended_price: float | None = None
    description: str | None
    status: ListingStatusEnum

    model_config = {"from_attributes": True}


class PriceRecommendationRequest(BaseModel):
    textbook_id: int
    condition: ConditionEnum


class PriceRecommendationOut(BaseModel):
    recommended_price: float
    rationale: str


class MatchOut(BaseModel):
    listing_id: int
    textbook_id: int
    score: float
    reason: str


class ConversationCreate(BaseModel):
    listing_id: int


class ConversationOut(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    status: str

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    is_agentic: bool
    sent_at: datetime

    model_config = {"from_attributes": True}

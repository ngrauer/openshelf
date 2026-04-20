"""
OpenShelf MVP v2 — Messaging Service

Shared helpers for conversations and messages:
- get_or_create_conversation: idempotent conversation lookup
- build_agentic_first_message: rule-based templated outreach (Phase A3)
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import (
    BookCondition,
    Conversation,
    ConversationStatus,
    Listing,
    Textbook,
    User,
)


def get_or_create_conversation(
    db: Session,
    listing_id: int,
    buyer_id: int,
    seller_id: int,
) -> Conversation:
    """Find or create a conversation for a (listing, buyer, seller) triple."""
    existing = (
        db.query(Conversation)
        .filter(
            Conversation.listing_id == listing_id,
            Conversation.buyer_id == buyer_id,
            Conversation.seller_id == seller_id,
        )
        .first()
    )
    if existing:
        return existing

    conversation = Conversation(
        listing_id=listing_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        status=ConversationStatus.pending,
    )
    db.add(conversation)
    db.flush()  # ensure conversation.id is populated for immediate use
    return conversation


# ============================================================
#  AGENTIC FIRST-MESSAGE TEMPLATES (rule-based; not LLM-generated)
# ============================================================

_CONDITION_PHRASING = {
    BookCondition.new: "looks brand new",
    BookCondition.like_new: "is in like-new condition",
    BookCondition.good: "is in good shape",
    BookCondition.fair: "is in fair condition",
    BookCondition.poor: "is well-worn",
}


def build_agentic_first_message(
    buyer: User,
    seller: User,
    listing: Listing,
    textbook: Optional[Textbook] = None,
) -> str:
    """Generate a polite, templated first message from a buyer to a seller.

    Not LLM-generated — this is a deterministic template. The real LLM
    integration is the chatbot (Phase B). Agentic outreach is scoped as
    mocked templates per the project spec.
    """
    title = textbook.title if textbook else "your textbook"
    condition_phrase = _CONDITION_PHRASING.get(listing.condition, "is listed")
    price_str = f"${listing.price:.2f}"

    return (
        f"Hi {seller.first_name}! I'm {buyer.first_name}, a student at "
        f"OpenShelf. I saw your listing for {title} ({price_str}) and noticed it "
        f"{condition_phrase}. Is it still available? I'd love to arrange a "
        f"campus meetup if it is. Thanks!"
    )

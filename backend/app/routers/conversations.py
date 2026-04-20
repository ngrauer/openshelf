"""
OpenShelf MVP v2 — Conversations Router

Spec-aligned conversation endpoints (POST /conversations, GET /conversations,
GET/POST /conversations/{id}/messages). These replace the v1 direct message
model for frontend use; the legacy /messages routes still work via a
backward-compat shim (see routers/messages.py).
"""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import (
    Conversation,
    ConversationStatus,
    Listing,
    Message,
    Notification,
    NotificationType,
    Textbook,
    User,
)
from app.schemas.schemas import (
    ConversationCreate,
    ConversationDetail,
    ConversationMessageCreate,
    ConversationOut,
    ConversationSummary,
    ListingOut,
    MessageOut,
    UserOut,
)
from app.services.auth_service import get_current_user
from app.services.messaging_service import (
    build_agentic_first_message,
    get_or_create_conversation,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


# ============================================================
#  CREATE / LIST
# ============================================================

@router.post("/", response_model=ConversationDetail, status_code=status.HTTP_201_CREATED)
def start_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start (or resume) a conversation about a listing.

    If `initial_message` is omitted, an agentic first-message template is
    generated for the buyer. Sellers cannot start conversations about their
    own listings.
    """
    listing = db.query(Listing).filter(Listing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot start a conversation on your own listing")

    seller = db.query(User).filter(User.id == listing.seller_id).first()
    textbook = db.query(Textbook).filter(Textbook.id == listing.textbook_id).first()

    conversation = get_or_create_conversation(
        db,
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.seller_id,
    )

    # Only send an initial message the first time the conversation is created.
    is_new = len(conversation.messages) == 0
    if is_new:
        content = payload.initial_message or build_agentic_first_message(
            buyer=current_user, seller=seller, listing=listing, textbook=textbook,
        )
        message = Message(
            conversation_id=conversation.id,
            sender_id=current_user.id,
            content=content,
            is_agentic=payload.is_agentic and payload.initial_message is None,
        )
        db.add(message)
        db.add(
            Notification(
                user_id=listing.seller_id,
                type=NotificationType.offer,
                content=f"{current_user.first_name} {current_user.last_name} is interested in your listing",
                reference_id=conversation.id,
            )
        )

    db.commit()
    db.refresh(conversation)

    return _serialize_conversation_detail(conversation)


@router.get("/", response_model=List[ConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List conversations for the current user (inbox view)."""
    conversations = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.listing).joinedload(Listing.textbook),
            joinedload(Conversation.buyer),
            joinedload(Conversation.seller),
            joinedload(Conversation.messages),
        )
        .filter(
            or_(
                Conversation.buyer_id == current_user.id,
                Conversation.seller_id == current_user.id,
            )
        )
        .all()
    )

    summaries: List[ConversationSummary] = []
    for c in conversations:
        is_buyer = current_user.id == c.buyer_id
        other_user = c.seller if is_buyer else c.buyer
        last_message = c.messages[-1] if c.messages else None
        unread_count = sum(
            1 for m in c.messages if m.sender_id != current_user.id and m.read_at is None
        )
        summaries.append(
            ConversationSummary(
                conversation=ConversationOut.model_validate(c),
                other_user=UserOut.model_validate(other_user),
                listing=ListingOut.model_validate(c.listing) if c.listing else None,
                last_message=MessageOut.model_validate(last_message) if last_message else None,
                unread_count=unread_count,
            )
        )

    # Most recent activity first.
    summaries.sort(
        key=lambda s: s.last_message.sent_at if s.last_message and s.last_message.sent_at else datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return summaries


# ============================================================
#  DETAIL / MESSAGES
# ============================================================

@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single conversation with its messages. Marks incoming as read."""
    conversation = _load_conversation(db, conversation_id, current_user)

    now = datetime.now(timezone.utc)
    for msg in conversation.messages:
        if msg.sender_id != current_user.id and msg.read_at is None:
            msg.read_at = now
    db.commit()
    db.refresh(conversation)

    return _serialize_conversation_detail(conversation)


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the message thread for a conversation (does NOT mark as read)."""
    conversation = _load_conversation(db, conversation_id, current_user)
    return conversation.messages


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
def post_conversation_message(
    conversation_id: int,
    payload: ConversationMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Append a message to an existing conversation."""
    conversation = _load_conversation(db, conversation_id, current_user)

    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        content=payload.content,
        is_agentic=payload.is_agentic,
    )
    db.add(message)

    if (
        conversation.status == ConversationStatus.pending
        and current_user.id == conversation.seller_id
    ):
        conversation.status = ConversationStatus.active

    # Notify the other participant.
    other_id = (
        conversation.seller_id
        if current_user.id == conversation.buyer_id
        else conversation.buyer_id
    )
    db.add(
        Notification(
            user_id=other_id,
            type=NotificationType.message,
            content=f"New message from {current_user.first_name} {current_user.last_name}",
            reference_id=conversation.id,
        )
    )

    db.commit()
    db.refresh(message)
    return message


# ============================================================
#  HELPERS
# ============================================================

def _load_conversation(db: Session, conversation_id: int, current_user: User) -> Conversation:
    conversation = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.listing).joinedload(Listing.textbook),
            joinedload(Conversation.buyer),
            joinedload(Conversation.seller),
            joinedload(Conversation.messages),
        )
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in (conversation.buyer_id, conversation.seller_id):
        raise HTTPException(status_code=403, detail="Not a participant in this conversation")
    return conversation


def _serialize_conversation_detail(conversation: Conversation) -> ConversationDetail:
    return ConversationDetail(
        id=conversation.id,
        listing_id=conversation.listing_id,
        buyer_id=conversation.buyer_id,
        seller_id=conversation.seller_id,
        status=conversation.status,
        created_at=conversation.created_at,
        buyer=UserOut.model_validate(conversation.buyer) if conversation.buyer else None,
        seller=UserOut.model_validate(conversation.seller) if conversation.seller else None,
        listing=ListingOut.model_validate(conversation.listing) if conversation.listing else None,
        messages=[MessageOut.model_validate(m) for m in conversation.messages],
    )

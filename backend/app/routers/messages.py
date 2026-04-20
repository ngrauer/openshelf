"""
OpenShelf MVP v2 — Messages Router (legacy compatibility layer)

v2 introduces a `conversations` table (see routers/conversations.py). These
endpoints are preserved so the v1 Swagger demo script keeps working: they
transparently resolve or create the underlying conversation.
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Conversation,
    ConversationStatus,
    Listing,
    Message,
    Notification,
    NotificationType,
    User,
)
from app.schemas.schemas import MessageCreate, MessageOut
from app.services.auth_service import get_current_user
from app.services.messaging_service import get_or_create_conversation

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message about a listing. Resolves/creates the conversation."""
    listing = db.query(Listing).filter(Listing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Figure out which side of the conversation the current user is on.
    if current_user.id == listing.seller_id:
        buyer_id, seller_id = payload.receiver_id, current_user.id
    else:
        buyer_id, seller_id = current_user.id, listing.seller_id

    conversation = get_or_create_conversation(
        db,
        listing_id=listing.id,
        buyer_id=buyer_id,
        seller_id=seller_id,
    )

    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        content=payload.content,
        is_agentic=payload.is_agentic,
    )
    db.add(message)

    # Promote pending conversations to active once the second party replies.
    if conversation.status == ConversationStatus.pending and current_user.id == conversation.seller_id:
        conversation.status = ConversationStatus.active

    notif = Notification(
        user_id=payload.receiver_id,
        type=NotificationType.message,
        content=f"New message from {current_user.first_name} {current_user.last_name}",
        reference_id=conversation.id,
    )
    db.add(notif)

    db.commit()
    db.refresh(message)
    return message


@router.get("/conversation/{user_id}/{other_user_id}", response_model=List[MessageOut])
def get_conversation_thread(
    user_id: int,
    other_user_id: int,
    listing_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get the message thread between two users, optionally scoped to a listing."""
    q = db.query(Conversation).filter(
        or_(
            and_(Conversation.buyer_id == user_id, Conversation.seller_id == other_user_id),
            and_(Conversation.buyer_id == other_user_id, Conversation.seller_id == user_id),
        )
    )
    if listing_id is not None:
        q = q.filter(Conversation.listing_id == listing_id)

    conversations = q.all()
    if not conversations:
        return []

    conversation_ids = [c.id for c in conversations]
    messages = (
        db.query(Message)
        .filter(Message.conversation_id.in_(conversation_ids))
        .order_by(Message.sent_at.asc())
        .all()
    )

    # Mark incoming messages as read.
    now = datetime.now(timezone.utc)
    for msg in messages:
        if msg.sender_id != user_id and msg.read_at is None:
            msg.read_at = now
    db.commit()

    return messages


@router.get("/inbox/{user_id}", response_model=List[MessageOut])
def get_inbox(user_id: int, db: Session = Depends(get_db)):
    """Get all messages in conversations where the user is buyer or seller."""
    conversation_ids = [
        c.id for c in db.query(Conversation.id)
        .filter(or_(Conversation.buyer_id == user_id, Conversation.seller_id == user_id))
        .all()
    ]
    if not conversation_ids:
        return []

    return (
        db.query(Message)
        .filter(Message.conversation_id.in_(conversation_ids))
        .order_by(Message.sent_at.desc())
        .all()
    )

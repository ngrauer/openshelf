from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Conversation, Listing, Message, User
from app.schemas.schemas import ConversationCreate, ConversationOut, MessageCreate, MessageOut

router = APIRouter(prefix="/api/conversations", tags=["messaging"])


@router.post("", response_model=ConversationOut)
def start_conversation(payload: ConversationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    listing = db.query(Listing).filter(Listing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    convo = Conversation(listing_id=listing.id, buyer_id=current_user.id, seller_id=listing.seller_id, status="active")
    db.add(convo)
    db.flush()
    agentic_msg = Message(
        conversation_id=convo.id,
        sender_id=current_user.id,
        content="Hi! I'm interested in your textbook listing. Is it still available?",
        is_agentic=True,
    )
    db.add(agentic_msg)
    db.commit()
    db.refresh(convo)
    return convo


@router.get("", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Conversation).filter((Conversation.buyer_id == current_user.id) | (Conversation.seller_id == current_user.id)).all()


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in (convo.buyer_id, convo.seller_id):
        raise HTTPException(status_code=403, detail="Not allowed")
    msg = Message(conversation_id=convo.id, sender_id=current_user.id, content=payload.content, is_agentic=False)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in (convo.buyer_id, convo.seller_id):
        raise HTTPException(status_code=403, detail="Not allowed")
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.sent_at.asc()).all()

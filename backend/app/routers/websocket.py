"""
OpenShelf MVP v2 — WebSocket Chat

Real-time chat endpoint for a single conversation. Simple in-memory
connection manager (single process, no Redis) — adequate for MVP and the
capstone demo environment.

Client flow:
    ws://localhost:8000/ws/chat/{conversation_id}?token=<jwt>

Message format (client → server):
    {"content": "hello", "is_agentic": false}

Message format (server → client):
    {"type": "message", "message": {<MessageOut>}}
    {"type": "error", "detail": "..."}
"""
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.models import (
    Conversation,
    ConversationStatus,
    Message,
    Notification,
    NotificationType,
    User,
)
from app.services.auth_service import resolve_user_from_token

router = APIRouter(tags=["WebSocket"])


# ============================================================
#  CONNECTION MANAGER
# ============================================================

class ConnectionManager:
    """Tracks open WebSocket connections per conversation.

    In-process only. If we ever run multiple workers we'll need Redis pub/sub,
    but for MVP/demo this is fine (uvicorn default is single worker).
    """

    def __init__(self) -> None:
        self._rooms: Dict[int, Set[WebSocket]] = defaultdict(set)

    async def connect(self, conversation_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._rooms[conversation_id].add(ws)

    def disconnect(self, conversation_id: int, ws: WebSocket) -> None:
        self._rooms[conversation_id].discard(ws)
        if not self._rooms[conversation_id]:
            self._rooms.pop(conversation_id, None)

    async def broadcast(self, conversation_id: int, payload: dict) -> None:
        """Send to every socket currently subscribed to this conversation."""
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(conversation_id, ())):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(conversation_id, ws)


manager = ConnectionManager()


# ============================================================
#  ENDPOINT
# ============================================================

@router.websocket("/ws/chat/{conversation_id}")
async def chat_ws(websocket: WebSocket, conversation_id: int, token: str = ""):
    """Real-time chat for a single conversation.

    Auth: JWT via `?token=` query param. Closes with 4401 on auth failure,
    4403 if user is not a participant, 4404 if the conversation is missing.
    """
    db: Session = SessionLocal()
    try:
        user = resolve_user_from_token(token, db) if token else None
        if user is None:
            await websocket.close(code=4401)
            return

        conversation = (
            db.query(Conversation).filter(Conversation.id == conversation_id).first()
        )
        if conversation is None:
            await websocket.close(code=4404)
            return
        if user.id not in (conversation.buyer_id, conversation.seller_id):
            await websocket.close(code=4403)
            return

        await manager.connect(conversation_id, websocket)

        try:
            while True:
                data = await websocket.receive_json()
                content = (data or {}).get("content", "").strip()
                if not content:
                    await websocket.send_json({"type": "error", "detail": "Empty message"})
                    continue
                is_agentic = bool((data or {}).get("is_agentic", False))

                # Re-resolve the conversation from this session (state may have changed).
                conversation = (
                    db.query(Conversation)
                    .filter(Conversation.id == conversation_id)
                    .first()
                )
                if conversation is None:
                    await websocket.send_json({"type": "error", "detail": "Conversation gone"})
                    break

                message = Message(
                    conversation_id=conversation.id,
                    sender_id=user.id,
                    content=content,
                    is_agentic=is_agentic,
                )
                db.add(message)

                # Promote pending → active on seller's first reply.
                if (
                    conversation.status == ConversationStatus.pending
                    and user.id == conversation.seller_id
                ):
                    conversation.status = ConversationStatus.active

                # Notification for the other party (always created, regardless of
                # whether they currently have a socket open).
                other_id = (
                    conversation.seller_id
                    if user.id == conversation.buyer_id
                    else conversation.buyer_id
                )
                db.add(
                    Notification(
                        user_id=other_id,
                        type=NotificationType.message,
                        content=f"New message from {user.first_name} {user.last_name}",
                        reference_id=conversation.id,
                    )
                )

                db.commit()
                db.refresh(message)

                payload = {
                    "type": "message",
                    "message": {
                        "id": message.id,
                        "conversation_id": message.conversation_id,
                        "sender_id": message.sender_id,
                        "content": message.content,
                        "is_agentic": message.is_agentic,
                        "read_at": message.read_at.isoformat() if message.read_at else None,
                        "sent_at": message.sent_at.isoformat() if message.sent_at else None,
                    },
                }
                await manager.broadcast(conversation_id, payload)
        except WebSocketDisconnect:
            pass
        finally:
            manager.disconnect(conversation_id, websocket)
    finally:
        db.close()

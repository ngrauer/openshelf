"""
OpenShelf MVP v2 — Chatbot Router

POST /chat — OpenShelf assistant endpoint.

This is the frontend integration point. The internals are pluggable:
Phase A scaffolds a template-based responder so the frontend can wire
against a stable contract. Phase B swaps in real RAG + Ollama without
changing the request/response shape.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.auth_service import get_current_user
from app.services.chatbot_service import generate_chat_response

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("/", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the OpenShelf assistant.

    Auth is required — the chatbot uses the caller's identity to personalize
    retrieval (e.g., "find me the CS 301 book" filters by the user's
    enrolled courses).
    """
    return generate_chat_response(db=db, user=current_user, request=payload)

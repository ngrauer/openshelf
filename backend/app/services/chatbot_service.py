"""
OpenShelf MVP v2 — Chatbot Service

Priority order for AI backends:
  1. Ollama (local Qwen model) — configured via OLLAMA_URL / OLLAMA_MODEL env vars
  2. Claude Haiku (Anthropic API) — configured via ANTHROPIC_API_KEY
  3. Template fallback — keyword-based, always available

Public surface: generate_chat_response(db, user, request) → ChatResponse
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import List

# Load .env file if present (supports ANTHROPIC_API_KEY and OLLAMA_* vars)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
except ImportError:
    pass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import (
    Conversation,
    Course,
    CourseTextbook,
    Enrollment,
    Listing,
    ListingStatus,
    Message,
    Review,
    Textbook,
    User,
)
from app.schemas.schemas import ChatRequest, ChatResponse, ChatSource
from app.services.chatbot_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")


# ============================================================
#  PUBLIC ENTRY POINT
# ============================================================

def generate_chat_response(db: Session, user: User, request: ChatRequest) -> ChatResponse:
    """Route a chat request: Ollama → Claude → template fallback."""
    # Build shared context once (used by both LLM backends)
    context_parts, sources = _build_context(db, user, request.message)
    rag_context = "\n\n".join(context_parts) if context_parts else "No specific data found."

    messages = [
        {"role": t.role, "content": t.content}
        for t in request.history
    ]
    messages.append({
        "role": "user",
        "content": (
            f"<database_context>\n{rag_context}\n</database_context>\n\n"
            f"User ({user.first_name} {user.last_name}, {user.email}):\n"
            f"{request.message}"
        ),
    })

    # 1. Try Ollama
    text = _try_ollama(messages)
    if text is not None:
        return ChatResponse(response=text, sources=sources, model=OLLAMA_MODEL)

    # 2. Try Claude
    text = _try_claude(messages)
    if text is not None:
        return ChatResponse(response=text, sources=sources, model="claude-haiku-4-5-20251001")

    # 3. Template fallback
    return _template_response(db, user, request)


# ============================================================
#  OLLAMA BACKEND
# ============================================================

def _try_ollama(messages: list) -> str | None:
    all_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": all_messages,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read())
        return data["message"]["content"]
    except Exception as e:
        logger.warning(f"Ollama unavailable ({OLLAMA_MODEL}): {e}")
        return None


# ============================================================
#  CLAUDE HAIKU BACKEND
# ============================================================

_anthropic_client = None


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is not None:
        return _anthropic_client
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
        return _anthropic_client
    except Exception as e:
        logger.warning(f"Anthropic client init failed: {e}")
        return None


def _try_claude(messages: list) -> str | None:
    client = _get_anthropic_client()
    if client is None:
        return None
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        return None


# ============================================================
#  CONTEXT BUILDING (shared by all LLM backends)
# ============================================================

_BOOK_INTENT_KEYWORDS = {
    "book", "textbook", "listing", "listings", "course", "courses", "buy", "sell",
    "find", "search", "available", "price", "cheap", "cost", "condition", "isbn",
    "author", "title", "required", "recommended", "need", "looking", "afford",
    "seller", "sellers", "class", "classes", "enrolled", "shopping",
}


def _has_book_intent(message: str) -> bool:
    words = set(message.lower().split())
    return bool(words & _BOOK_INTENT_KEYWORDS)


def _build_context(db: Session, user: User, message: str) -> tuple[list[str], list[ChatSource]]:
    """Build RAG context parts and source citations for the given user message."""
    parts: list[str] = []
    sources: list[ChatSource] = []

    unread_text = _get_unread_summary(db, user)
    if unread_text:
        parts.append("## Messaging Status\n" + unread_text)

    if not _has_book_intent(message):
        return parts, sources

    courses_text = _get_user_courses(db, user)
    if courses_text:
        parts.append("## User's Enrolled Courses\n" + courses_text)

    listings_text = _get_course_listings(db, user)
    if listings_text:
        parts.append("## Available Listings for User's Courses (with seller credibility)\n" + listings_text)

    search_text = _search_listings(db, message)
    if search_text:
        parts.append("## Search Results Matching User's Query\n" + search_text)

    sources = _extract_sources(db, user, message)
    return parts, sources


def _get_user_courses(db: Session, user: User) -> str:
    rows = (
        db.query(Course, Textbook, CourseTextbook.is_required)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .join(CourseTextbook, CourseTextbook.course_id == Course.id)
        .join(Textbook, Textbook.id == CourseTextbook.textbook_id)
        .filter(Enrollment.user_id == user.id)
        .order_by(Course.course_code)
        .all()
    )
    if not rows:
        return ""
    lines = []
    for course, textbook, is_required in rows:
        req = "Required" if is_required else "Recommended"
        lines.append(
            f"- {course.course_code} ({course.course_name}): "
            f'"{textbook.title}" by {textbook.author} — '
            f"Retail ${textbook.retail_price:.2f} [{req}]"
        )
    return "\n".join(lines)


def _get_seller_ratings(db: Session, seller_ids: list[int]) -> dict[int, tuple[float, int]]:
    """Return {seller_id: (avg_rating, review_count)} for the given seller IDs."""
    if not seller_ids:
        return {}
    rows = (
        db.query(
            Review.reviewed_user_id,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .filter(Review.reviewed_user_id.in_(seller_ids))
        .group_by(Review.reviewed_user_id)
        .all()
    )
    return {r.reviewed_user_id: (round(float(r.avg_rating), 1), r.review_count) for r in rows}


def _format_seller_credibility(seller: User, ratings: dict) -> str:
    if seller.id in ratings:
        avg, count = ratings[seller.id]
        return f"{seller.first_name} {seller.last_name} ({avg} stars, {count} review{'s' if count != 1 else ''})"
    return f"{seller.first_name} {seller.last_name} (new seller)"


def _get_course_listings(db: Session, user: User) -> str:
    course_ids = [
        e.course_id for e in db.query(Enrollment.course_id)
        .filter(Enrollment.user_id == user.id)
        .all()
    ]
    if not course_ids:
        return ""

    textbook_ids = [
        ct.textbook_id for ct in db.query(CourseTextbook.textbook_id)
        .filter(CourseTextbook.course_id.in_(course_ids))
        .all()
    ]
    if not textbook_ids:
        return ""

    rows = (
        db.query(Listing, Textbook, User)
        .join(Textbook, Listing.textbook_id == Textbook.id)
        .join(User, Listing.seller_id == User.id)
        .filter(
            Listing.textbook_id.in_(textbook_ids),
            Listing.status == ListingStatus.active,
            Listing.seller_id != user.id,
        )
        .order_by(Textbook.title, Listing.price)
        .all()
    )
    if not rows:
        return ""

    seller_ids = list({seller.id for _, _, seller in rows})
    ratings = _get_seller_ratings(db, seller_ids)

    lines = []
    for listing, textbook, seller in rows:
        seller_info = _format_seller_credibility(seller, ratings)
        lines.append(
            f'- "{textbook.title}" — ${listing.price:.2f} ({listing.condition.value}) '
            f"by {seller_info} "
            f"[Listing #{listing.id}, Retail: ${textbook.retail_price:.2f}]"
        )
    return "\n".join(lines)


_SEARCH_STOP_WORDS = {
    "i", "me", "my", "a", "an", "the", "is", "are", "was", "were",
    "do", "does", "did", "can", "could", "would", "should", "have",
    "has", "had", "for", "of", "to", "in", "on", "at", "by", "and",
    "or", "but", "not", "any", "all", "this", "that", "what", "how",
    "find", "get", "buy", "sell", "need", "want", "looking", "search",
    "show", "tell", "about", "much", "price", "cost", "available",
    "there", "here", "it", "its", "with", "from",
}


def _search_listing_rows(db: Session, query: str) -> list:
    """Return (Listing, Textbook, User) rows matching query keywords, or [] if none."""
    words = [w for w in query.lower().split() if len(w) > 2 and w not in _SEARCH_STOP_WORDS]
    if not words:
        return []

    from sqlalchemy import or_
    conditions = []
    for word in words[:3]:
        conditions.append(Textbook.title.ilike(f"%{word}%"))
        conditions.append(Textbook.author.ilike(f"%{word}%"))

    matching_textbooks = db.query(Textbook).filter(or_(*conditions)).limit(10).all()
    if not matching_textbooks:
        return []

    tb_ids = [t.id for t in matching_textbooks]
    return (
        db.query(Listing, Textbook, User)
        .join(Textbook, Listing.textbook_id == Textbook.id)
        .join(User, Listing.seller_id == User.id)
        .filter(Listing.textbook_id.in_(tb_ids), Listing.status == ListingStatus.active)
        .order_by(Listing.price)
        .limit(10)
        .all()
    )


def _search_listings(db: Session, query: str) -> str:
    rows = _search_listing_rows(db, query)
    if not rows:
        return ""

    seller_ids = list({seller.id for _, _, seller in rows})
    ratings = _get_seller_ratings(db, seller_ids)

    lines = []
    for listing, textbook, seller in rows:
        seller_info = _format_seller_credibility(seller, ratings)
        lines.append(
            f'- "{textbook.title}" — ${listing.price:.2f} ({listing.condition.value}) '
            f"by {seller_info} [Listing #{listing.id}]"
        )
    return "\n".join(lines) if lines else "No active listings found for matching textbooks."


def _get_unread_summary(db: Session, user: User) -> str:
    unread_count = (
        db.query(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(
            (Conversation.buyer_id == user.id) | (Conversation.seller_id == user.id),
            Message.sender_id != user.id,
            Message.read_at.is_(None),
        )
        .count()
    )
    if unread_count == 0:
        return "User has no unread messages."
    return f"User has {unread_count} unread message{'s' if unread_count != 1 else ''} waiting in their inbox."


def _extract_sources(db: Session, user: User, message: str) -> List[ChatSource]:
    # Prefer search-matched listings as sources; fall back to enrolled-course listings.
    search_rows = _search_listing_rows(db, message)
    if search_rows:
        return [
            ChatSource(
                kind="listing",
                title=textbook.title,
                snippet=f"${listing.price:.2f}, {listing.condition.value} condition",
                reference_id=listing.id,
            )
            for listing, textbook, _ in search_rows[:5]
        ]

    # Generic book query — show cheapest listings for the user's courses.
    course_ids = [
        e.course_id for e in db.query(Enrollment.course_id)
        .filter(Enrollment.user_id == user.id)
        .all()
    ]
    if not course_ids:
        return []

    textbook_ids = [
        ct.textbook_id for ct in db.query(CourseTextbook.textbook_id)
        .filter(CourseTextbook.course_id.in_(course_ids))
        .all()
    ]
    rows = (
        db.query(Listing, Textbook)
        .join(Textbook, Listing.textbook_id == Textbook.id)
        .filter(
            Listing.textbook_id.in_(textbook_ids),
            Listing.status == ListingStatus.active,
            Listing.seller_id != user.id,
        )
        .order_by(Listing.price)
        .limit(5)
        .all()
    )
    return [
        ChatSource(
            kind="listing",
            title=textbook.title,
            snippet=f"${listing.price:.2f}, {listing.condition.value} condition",
            reference_id=listing.id,
        )
        for listing, textbook in rows
    ]


# ============================================================
#  TEMPLATE FALLBACK
# ============================================================

_GREETING_KEYWORDS = {"hi", "hello", "hey", "yo", "sup"}
_LISTING_KEYWORDS = {"find", "buy", "book", "textbook", "cheap", "available"}
_PRICING_KEYWORDS = {"price", "worth", "sell for", "how much"}
_HOWTO_KEYWORDS = {"how do i", "how to", "where do i"}


def _template_response(db: Session, user: User, request: ChatRequest) -> ChatResponse:
    msg = request.message.lower().strip()
    sources: List[ChatSource] = []

    if any(kw in msg for kw in _GREETING_KEYWORDS) and len(msg) < 40:
        text = (
            f"Hi {user.first_name}! I'm the OpenShelf assistant. I can help you "
            "find textbooks for your courses, explain pricing, and walk you "
            "through how the platform works. What do you need?"
        )
        return ChatResponse(response=text, sources=sources, model="template")

    if any(kw in msg for kw in _HOWTO_KEYWORDS):
        text = (
            "On OpenShelf you can:\n"
            "- Browse listings from the Shopping tab, filtered to your enrolled courses\n"
            "- Click Contact Seller to open a chat (the first message is AI-drafted)\n"
            "- List your own books from the My Listings tab — we'll suggest a price\n"
            "- Leave reviews after a transaction completes\n"
            "What would you like to do first?"
        )
        return ChatResponse(response=text, sources=sources, model="template")

    if any(kw in msg for kw in _PRICING_KEYWORDS):
        text = (
            "OpenShelf's AI price recommendation starts from the textbook's "
            "retail MSRP, applies a condition multiplier (new 85%, like new 70%, "
            "good 55%, fair 40%, poor 25%), then blends 60/40 with the average "
            "price of existing listings for the same book."
        )
        return ChatResponse(response=text, sources=sources, model="template")

    if any(kw in msg for kw in _LISTING_KEYWORDS):
        listings = _find_listings_for_user(db, user, limit=3)
        if not listings:
            text = (
                "I couldn't find any active listings tied to your enrolled "
                "courses yet. Try browsing all listings from the Shopping tab."
            )
            return ChatResponse(response=text, sources=sources, model="template")

        seller_ids = [l.seller_id for l, _ in listings]
        ratings = _get_seller_ratings(db, seller_ids)

        lines = [f"Here are the top matches for your courses, {user.first_name}:"]
        for l, t in listings:
            seller_info = _format_seller_credibility(
                db.query(User).filter(User.id == l.seller_id).first(), ratings
            )
            lines.append(f"- {t.title} — ${l.price:.2f} ({l.condition.value}) by {seller_info} [Listing #{l.id}]")
            sources.append(
                ChatSource(
                    kind="listing",
                    title=t.title,
                    snippet=f"${l.price:.2f}, {l.condition.value} condition",
                    reference_id=l.id,
                )
            )
        return ChatResponse(response="\n".join(lines), sources=sources, model="template")

    text = (
        "I'm the OpenShelf assistant — ask me about finding textbooks for your "
        "courses, listing a book, pricing, or how the platform works."
    )
    return ChatResponse(response=text, sources=sources, model="template")


def _find_listings_for_user(db: Session, user: User, limit: int = 5):
    course_ids = [
        e.course_id for e in db.query(Enrollment.course_id)
        .filter(Enrollment.user_id == user.id)
        .all()
    ]
    if not course_ids:
        return []

    textbook_ids = [
        ct.textbook_id for ct in db.query(CourseTextbook.textbook_id)
        .filter(CourseTextbook.course_id.in_(course_ids))
        .all()
    ]
    if not textbook_ids:
        return []

    return (
        db.query(Listing, Textbook)
        .join(Textbook, Listing.textbook_id == Textbook.id)
        .filter(
            Listing.textbook_id.in_(textbook_ids),
            Listing.status == ListingStatus.active,
            Listing.seller_id != user.id,
        )
        .order_by(Listing.price.asc())
        .limit(limit)
        .all()
    )

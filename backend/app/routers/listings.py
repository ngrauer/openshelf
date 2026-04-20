"""
OpenShelf MVP v1 — Listings Router
Create, search, update, delete listings. AI price recommendation.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    Listing, Textbook, CourseTextbook, User, ListingStatus, BookCondition,
    Conversation, Notification, NotificationType, ConversationStatus,
)
from app.schemas.schemas import (
    ListingCreate, ListingUpdate, ListingOut, ListingDetail,
    AIPriceRequest, AIPriceResponse, UserOut, TextbookOut,
)
from app.services.auth_service import get_current_user
from app.services.matching_engine import get_ai_price_recommendation

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("/", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new listing with automatic AI price recommendation."""
    # Validate textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == payload.textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")

    # Generate AI price recommendation
    rec = get_ai_price_recommendation(db, payload.textbook_id, payload.condition)

    urls = payload.image_urls or ([payload.image_url] if payload.image_url else [])
    listing = Listing(
        seller_id=current_user.id,
        textbook_id=payload.textbook_id,
        condition=payload.condition,
        price=payload.price,
        ai_recommended_price=rec["recommended_price"],
        description=payload.description,
        image_url=urls[0] if urls else None,
        image_urls=urls,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/", response_model=List[ListingDetail])
def search_listings(
    course_id: Optional[int] = Query(None, description="Filter by course — returns listings for textbooks required by this course"),
    seller_id: Optional[int] = Query(None, description="Filter by seller"),
    isbn: Optional[str] = Query(None),
    title: Optional[str] = Query(None, description="Partial textbook title search"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    condition: Optional[BookCondition] = Query(None),
    status_filter: ListingStatus = Query(ListingStatus.active, alias="status"),
    db: Session = Depends(get_db),
):
    """Search and filter listings with multiple criteria."""
    q = (
        db.query(Listing)
        .options(
            joinedload(Listing.seller),
            joinedload(Listing.textbook),
        )
        .filter(Listing.status == status_filter)
    )

    # Filter by seller
    if seller_id:
        q = q.filter(Listing.seller_id == seller_id)

    # Filter by course (join through course_textbooks)
    if course_id:
        textbook_ids = (
            select(CourseTextbook.textbook_id)
            .where(CourseTextbook.course_id == course_id)
        )
        q = q.filter(Listing.textbook_id.in_(textbook_ids))

    # Filter by ISBN
    if isbn:
        textbook = db.query(Textbook).filter(Textbook.isbn == isbn).first()
        if textbook:
            q = q.filter(Listing.textbook_id == textbook.id)
        else:
            return []  # no textbook with that ISBN

    # Filter by title (partial match)
    if title:
        matching_ids = (
            select(Textbook.id)
            .where(Textbook.title.ilike(f"%{title}%"))
        )
        q = q.filter(Listing.textbook_id.in_(matching_ids))

    # Price range
    if min_price is not None:
        q = q.filter(Listing.price >= min_price)
    if max_price is not None:
        q = q.filter(Listing.price <= max_price)

    # Condition
    if condition:
        q = q.filter(Listing.condition == condition)

    listings = q.order_by(Listing.created_at.desc()).all()

    result = []
    for l in listings:
        result.append(ListingDetail(
            id=l.id,
            seller_id=l.seller_id,
            textbook_id=l.textbook_id,
            condition=l.condition,
            price=l.price,
            ai_recommended_price=l.ai_recommended_price,
            description=l.description,
            image_url=l.image_url,
            image_urls=l.image_urls or [],
            status=l.status,
            created_at=l.created_at,
            updated_at=l.updated_at,
            seller=UserOut.model_validate(l.seller) if l.seller else None,
            textbook=TextbookOut.model_validate(l.textbook) if l.textbook else None,
        ))
    return result


@router.get("/{listing_id}", response_model=ListingDetail)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a single listing with seller and textbook details."""
    listing = (
        db.query(Listing)
        .options(joinedload(Listing.seller), joinedload(Listing.textbook))
        .filter(Listing.id == listing_id)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingDetail(
        id=listing.id,
        seller_id=listing.seller_id,
        textbook_id=listing.textbook_id,
        condition=listing.condition,
        price=listing.price,
        ai_recommended_price=listing.ai_recommended_price,
        description=listing.description,
        image_url=listing.image_url,
        image_urls=listing.image_urls or [],
        status=listing.status,
        created_at=listing.created_at,
        updated_at=listing.updated_at,
        seller=UserOut.model_validate(listing.seller) if listing.seller else None,
        textbook=TextbookOut.model_validate(listing.textbook) if listing.textbook else None,
    )


@router.put("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a listing (owner only)."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your listing")

    was_active = listing.status == ListingStatus.active

    update_data = payload.model_dump(exclude_unset=True)
    # Keep image_url in sync with first item of image_urls
    if "image_urls" in update_data:
        urls = update_data["image_urls"] or []
        update_data["image_url"] = urls[0] if urls else update_data.get("image_url")
    for field, value in update_data.items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)

    # If status just changed to sold, notify buyer and seller to leave reviews
    if was_active and listing.status == ListingStatus.sold:
        _create_review_notifications(db, listing)

    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a listing (sets status to removed)."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    listing.status = ListingStatus.removed
    db.commit()


def _create_review_notifications(db: Session, listing: Listing):
    """Create review-prompt notifications for buyer and seller after a sale."""
    textbook = db.query(Textbook).filter(Textbook.id == listing.textbook_id).first()
    title = textbook.title if textbook else "a textbook"

    # Find the buyer from the most recent active conversation on this listing
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.listing_id == listing.id,
            Conversation.status.in_([ConversationStatus.active, ConversationStatus.completed]),
        )
        .order_by(Conversation.created_at.desc())
        .first()
    )

    seller = db.query(User).filter(User.id == listing.seller_id).first()

    if conversation:
        buyer = db.query(User).filter(User.id == conversation.buyer_id).first()
        if buyer:
            db.add(Notification(
                user_id=buyer.id,
                type=NotificationType.offer,
                content=f"Your purchase of \"{title}\" is complete! Rate {seller.first_name} {seller.last_name} as a seller.",
                reference_id=listing.id,
                is_read=False,
            ))
        # Mark conversation as completed
        conversation.status = ConversationStatus.completed

    if seller:
        buyer_name = f"{buyer.first_name} {buyer.last_name}" if conversation and buyer else "the buyer"
        db.add(Notification(
            user_id=seller.id,
            type=NotificationType.offer,
            content=f"Your listing for \"{title}\" has been marked as sold! Rate {buyer_name}.",
            reference_id=listing.id,
            is_read=False,
        ))

    db.commit()


@router.post("/ai-price", response_model=AIPriceResponse)
def ai_price_recommendation(
    payload: AIPriceRequest,
    db: Session = Depends(get_db),
):
    """Get an AI-generated price recommendation for a textbook in a given condition."""
    result = get_ai_price_recommendation(db, payload.textbook_id, payload.condition)
    return AIPriceResponse(**result)

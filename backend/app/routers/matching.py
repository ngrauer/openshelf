"""
OpenShelf MVP v1 — Matching Router
Generate and retrieve buyer-to-listing matches.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.models import Match, Listing, User
from app.schemas.schemas import (
    MatchOut, MatchDetail, MatchGenerateResponse,
    ListingDetail, UserOut, TextbookOut,
)
from app.services.auth_service import get_current_user
from app.services.matching_engine import generate_matches_for_user

router = APIRouter(prefix="/matches", tags=["Matching Engine"])


@router.post("/generate/{user_id}", response_model=MatchGenerateResponse)
def generate_matches(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Run the rule-based matching engine for a buyer.
    Finds active listings matching the buyer's enrolled courses
    and scores them based on condition, price, and recency.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_matches = generate_matches_for_user(db, user_id)

    # Reload all matches with full details
    all_matches = (
        db.query(Match)
        .options(
            joinedload(Match.listing).joinedload(Listing.seller),
            joinedload(Match.listing).joinedload(Listing.textbook),
        )
        .filter(Match.buyer_id == user_id)
        .order_by(Match.match_score.desc())
        .all()
    )

    match_details = []
    for m in all_matches:
        listing = m.listing
        match_details.append(MatchDetail(
            id=m.id,
            listing_id=m.listing_id,
            buyer_id=m.buyer_id,
            match_score=m.match_score,
            matched_at=m.matched_at,
            listing=ListingDetail(
                id=listing.id,
                seller_id=listing.seller_id,
                textbook_id=listing.textbook_id,
                condition=listing.condition,
                price=listing.price,
                ai_recommended_price=listing.ai_recommended_price,
                description=listing.description,
                status=listing.status,
                created_at=listing.created_at,
                updated_at=listing.updated_at,
                seller=UserOut.model_validate(listing.seller) if listing.seller else None,
                textbook=TextbookOut.model_validate(listing.textbook) if listing.textbook else None,
            ) if listing else None,
        ))

    return MatchGenerateResponse(
        user_id=user_id,
        matches_generated=len(new_matches),
        matches=match_details,
    )


@router.get("/{user_id}", response_model=List[MatchDetail])
def get_user_matches(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get all existing matches for a buyer, sorted by score descending."""
    matches = (
        db.query(Match)
        .options(
            joinedload(Match.listing).joinedload(Listing.seller),
            joinedload(Match.listing).joinedload(Listing.textbook),
        )
        .filter(Match.buyer_id == user_id)
        .order_by(Match.match_score.desc())
        .all()
    )

    result = []
    for m in matches:
        listing = m.listing
        result.append(MatchDetail(
            id=m.id,
            listing_id=m.listing_id,
            buyer_id=m.buyer_id,
            match_score=m.match_score,
            matched_at=m.matched_at,
            listing=ListingDetail(
                id=listing.id,
                seller_id=listing.seller_id,
                textbook_id=listing.textbook_id,
                condition=listing.condition,
                price=listing.price,
                ai_recommended_price=listing.ai_recommended_price,
                description=listing.description,
                status=listing.status,
                created_at=listing.created_at,
                updated_at=listing.updated_at,
                seller=UserOut.model_validate(listing.seller) if listing.seller else None,
                textbook=TextbookOut.model_validate(listing.textbook) if listing.textbook else None,
            ) if listing else None,
        ))
    return result

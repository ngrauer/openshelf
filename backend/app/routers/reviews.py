"""
OpenShelf MVP v1 — Reviews Router
Submit and retrieve user reviews.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.models import Review, User, Listing
from app.schemas.schemas import ReviewCreate, ReviewOut, ReviewWithReviewer, UserOut, UserProfile
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review for a user after a transaction."""
    # Can't review yourself
    if payload.reviewed_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot review yourself")

    # Check listing exists
    listing = db.query(Listing).filter(Listing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Check for duplicate review
    existing = db.query(Review).filter(
        Review.reviewer_id == current_user.id,
        Review.listing_id == payload.listing_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this transaction")

    review = Review(
        reviewer_id=current_user.id,
        reviewed_user_id=payload.reviewed_user_id,
        listing_id=payload.listing_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/user/{user_id}", response_model=List[ReviewWithReviewer])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a user."""
    reviews = (
        db.query(Review)
        .options(joinedload(Review.reviewer))
        .filter(Review.reviewed_user_id == user_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    result = []
    for r in reviews:
        result.append(ReviewWithReviewer(
            id=r.id,
            reviewer_id=r.reviewer_id,
            reviewed_user_id=r.reviewed_user_id,
            listing_id=r.listing_id,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at,
            reviewer=UserOut.model_validate(r.reviewer) if r.reviewer else None,
        ))
    return result


@router.get("/user/{user_id}/profile", response_model=UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile with aggregated review stats."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Aggregate stats
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.reviewed_user_id == user_id).scalar()
    total_reviews = db.query(func.count(Review.id)).filter(Review.reviewed_user_id == user_id).scalar()
    active_listings = db.query(func.count(Listing.id)).filter(
        Listing.seller_id == user_id, Listing.status == "active"
    ).scalar()

    return UserProfile(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        university_id=user.university_id,
        is_verified=user.is_verified,
        created_at=user.created_at,
        average_rating=round(avg_rating, 2) if avg_rating else None,
        total_reviews=total_reviews or 0,
        active_listings=active_listings or 0,
    )

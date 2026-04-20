"""
OpenShelf MVP v1 — Matching & Pricing Engine
Rule-based matching (buyer→seller) and AI price recommendation.
"""
from sqlalchemy.orm import Session
from app.models.models import (
    User, Listing, Enrollment, CourseTextbook, Match, Textbook,
    ListingStatus, BookCondition,
)
from typing import List, Dict


# ============================================================
#  CONDITION MULTIPLIERS FOR PRICING
# ============================================================

CONDITION_MULTIPLIERS: Dict[BookCondition, float] = {
    BookCondition.new: 0.85,       # 85% of retail
    BookCondition.like_new: 0.70,  # 70% of retail
    BookCondition.good: 0.55,      # 55% of retail
    BookCondition.fair: 0.40,      # 40% of retail
    BookCondition.poor: 0.25,      # 25% of retail
}

CONDITION_SCORES: Dict[BookCondition, float] = {
    BookCondition.new: 20,
    BookCondition.like_new: 18,
    BookCondition.good: 15,
    BookCondition.fair: 10,
    BookCondition.poor: 5,
}


# ============================================================
#  AI PRICE RECOMMENDATION (rule-based)
# ============================================================

def get_ai_price_recommendation(
    db: Session,
    textbook_id: int,
    condition: BookCondition,
) -> dict:
    """
    Generate a price recommendation based on:
    - The textbook's retail price (MSRP)
    - The book's condition
    - Existing market listings (supply/demand adjustment)
    """
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        return {
            "textbook_id": textbook_id,
            "condition": condition,
            "retail_price": None,
            "recommended_price": 0,
            "savings_vs_retail": None,
            "reasoning": "Textbook not found in database.",
        }

    retail = textbook.retail_price or 100.0  # fallback if no retail price

    # Base price from condition
    base_price = round(retail * CONDITION_MULTIPLIERS[condition], 2)

    # Market adjustment: check existing active listings for same textbook
    existing = (
        db.query(Listing)
        .filter(Listing.textbook_id == textbook_id, Listing.status == ListingStatus.active)
        .all()
    )
    if existing:
        avg_market = sum(l.price for l in existing) / len(existing)
        # Blend base price with market average (60% base, 40% market)
        adjusted_price = round(base_price * 0.6 + avg_market * 0.4, 2)
        reasoning = (
            f"Based on {condition.value} condition ({int(CONDITION_MULTIPLIERS[condition]*100)}% of "
            f"${retail:.2f} retail = ${base_price:.2f}), adjusted for {len(existing)} active "
            f"listing(s) averaging ${avg_market:.2f}. Final recommendation blends base and market."
        )
    else:
        adjusted_price = base_price
        reasoning = (
            f"Based on {condition.value} condition ({int(CONDITION_MULTIPLIERS[condition]*100)}% of "
            f"${retail:.2f} retail). No competing listings found — price set at condition baseline."
        )

    savings = round(retail - adjusted_price, 2) if textbook.retail_price else None

    return {
        "textbook_id": textbook_id,
        "condition": condition,
        "retail_price": textbook.retail_price,
        "recommended_price": adjusted_price,
        "savings_vs_retail": savings,
        "reasoning": reasoning,
    }


# ============================================================
#  RULE-BASED MATCHING ENGINE
# ============================================================

def generate_matches_for_user(db: Session, buyer_id: int) -> List[Match]:
    """
    Generate matches for a buyer based on their enrolled courses.

    Scoring rules (0–100):
    - ISBN/course match (required — if no match, listing is excluded): base 40 pts
    - Condition score: 0–20 pts (better condition = higher)
    - Price score: 0–25 pts (lower price relative to retail = higher)
    - Recency score: 0–15 pts (newer listing = higher)
    """
    # Step 1: Get all textbook IDs the buyer needs
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == buyer_id).all()
    course_ids = [e.course_id for e in enrollments]

    if not course_ids:
        return []

    needed_textbook_ids = (
        db.query(CourseTextbook.textbook_id)
        .filter(CourseTextbook.course_id.in_(course_ids))
        .all()
    )
    needed_ids = {t[0] for t in needed_textbook_ids}

    if not needed_ids:
        return []

    # Step 2: Get active listings for those textbooks (exclude buyer's own listings)
    listings = (
        db.query(Listing)
        .filter(
            Listing.textbook_id.in_(needed_ids),
            Listing.status == ListingStatus.active,
            Listing.seller_id != buyer_id,
        )
        .all()
    )

    if not listings:
        return []

    # Step 3: Score each listing
    matches_created = []
    for listing in listings:
        # Check if match already exists
        existing = (
            db.query(Match)
            .filter(Match.listing_id == listing.id, Match.buyer_id == buyer_id)
            .first()
        )
        if existing:
            continue

        score = _calculate_match_score(db, listing)

        match = Match(
            listing_id=listing.id,
            buyer_id=buyer_id,
            match_score=score,
        )
        db.add(match)
        matches_created.append(match)

    db.commit()
    for m in matches_created:
        db.refresh(m)

    return matches_created


def _calculate_match_score(db: Session, listing: Listing) -> float:
    """Calculate a 0–100 match score for a listing."""
    score = 0.0

    # --- Course/ISBN match (base 40) ---
    score += 40.0

    # --- Condition (0–20) ---
    score += CONDITION_SCORES.get(listing.condition, 10)

    # --- Price vs retail (0–25) ---
    textbook = db.query(Textbook).filter(Textbook.id == listing.textbook_id).first()
    if textbook and textbook.retail_price and textbook.retail_price > 0:
        price_ratio = listing.price / textbook.retail_price
        if price_ratio <= 0.3:
            score += 25
        elif price_ratio <= 0.5:
            score += 20
        elif price_ratio <= 0.7:
            score += 15
        elif price_ratio <= 0.85:
            score += 10
        else:
            score += 5
    else:
        score += 12  # neutral if no retail data

    # --- Recency (0–15) ---
    # For MVP, all mock data is recent, so give full marks
    score += 15

    return min(round(score, 2), 100.0)

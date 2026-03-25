from sqlalchemy.orm import Session

from app.models.models import CourseTextbook, Enrollment, Listing, ListingStatusEnum, Textbook


def get_recommendations(db: Session, buyer_id: int) -> list[dict]:
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == buyer_id).all()
    course_ids = [e.course_id for e in enrollments]
    if not course_ids:
        return []

    required = db.query(CourseTextbook).filter(CourseTextbook.course_id.in_(course_ids)).all()
    required_book_ids = {r.textbook_id for r in required}
    listings = (
        db.query(Listing)
        .filter(Listing.status == ListingStatusEnum.active, Listing.textbook_id.in_(required_book_ids), Listing.seller_id != buyer_id)
        .all()
    )

    result = []
    for listing in listings:
        textbook = db.query(Textbook).filter(Textbook.id == listing.textbook_id).first()
        score = 0.0
        reasons: list[str] = []

        if listing.textbook_id in required_book_ids:
            score += 60
            reasons.append("Required course textbook")

        # Budget sensitivity: lower price relative to retail = higher score (max 30)
        if textbook and float(textbook.retail_price) > 0:
            price_ratio = min(float(listing.price) / float(textbook.retail_price), 1)
            budget_score = round((1 - price_ratio) * 30, 2)
            score += budget_score
            reasons.append(f"Budget fit +{budget_score}")

        # Condition quality weight (max 10)
        condition_score_map = {"new": 10, "like_new": 8, "good": 6, "fair": 4, "poor": 2}
        cscore = condition_score_map[listing.condition.value]
        score += cscore
        reasons.append(f"Condition +{cscore}")

        result.append(
            {
                "listing_id": listing.id,
                "textbook_id": listing.textbook_id,
                "score": round(min(score, 100), 2),
                "reason": "; ".join(reasons),
            }
        )

    return sorted(result, key=lambda x: x["score"], reverse=True)

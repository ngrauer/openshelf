from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Listing, ListingStatusEnum, Textbook, User
from app.schemas.schemas import ListingCreate, ListingOut
from app.services.pricing import recommend_price

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.post("", response_model=ListingOut)
def create_listing(payload: ListingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    textbook = db.query(Textbook).filter(Textbook.id == payload.textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    rec, _ = recommend_price(float(textbook.retail_price), payload.condition)
    listing = Listing(
        seller_id=current_user.id,
        textbook_id=payload.textbook_id,
        condition=payload.condition,
        price=payload.price,
        ai_recommended_price=rec,
        description=payload.description,
        status=ListingStatusEnum.active,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("", response_model=list[ListingOut])
def search_listings(
    db: Session = Depends(get_db),
    course_id: int | None = None,
    isbn: str | None = None,
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    condition: str | None = None,
    status: ListingStatusEnum = ListingStatusEnum.active,
):
    query = db.query(Listing).join(Textbook, Textbook.id == Listing.textbook_id).filter(Listing.status == status)
    if isbn:
        query = query.filter(Textbook.isbn == isbn)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if condition:
        query = query.filter(Listing.condition == condition)
    # course_id filter intentionally simplified for v1 via textbook mappings (optional in v1)
    _ = course_id
    return query.order_by(Listing.price.asc()).all()

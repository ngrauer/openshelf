from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import ConditionEnum, Textbook
from app.schemas.schemas import PriceRecommendationOut
from app.services.pricing import recommend_price

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/price-recommendation", response_model=PriceRecommendationOut)
def price_recommendation(textbook_id: int, condition: ConditionEnum, db: Session = Depends(get_db)):
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    rec, rationale = recommend_price(float(textbook.retail_price), condition=condition)
    return PriceRecommendationOut(recommended_price=rec, rationale=rationale)

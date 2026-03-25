from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import MatchOut
from app.services.matching import get_recommendations

router = APIRouter(prefix="/api/matches", tags=["matching"])


@router.get("/recommendations", response_model=list[MatchOut])
def recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_recommendations(db, current_user.id)

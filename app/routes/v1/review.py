from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import get_db
from app.auth.jwt_bearer import get_current_user
from app.services import service
from app.models.schemas import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=201)
async def review_a_stay(
    review: ReviewCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [Guest] Konaklama icin yorum yap.
    Requires: JWT token
    Sadece rezervasyonu yapan kisi yorum yapabilir.
    Bir rezervasyona birden fazla yorum yapilamaz.
    """
    return service.create_review(db, review, user["user_id"])

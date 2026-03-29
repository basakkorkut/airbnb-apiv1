from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import get_db
from app.auth.jwt_bearer import get_current_user
from app.services import service
from app.models.schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
async def book_a_stay(
    booking: BookingCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [Guest] Bir listing'i rezerve et.
    Requires: JWT token
    Tarih cakismasi varsa 409 hatasi doner.
    """
    return service.create_booking(db, booking, user["user_id"])

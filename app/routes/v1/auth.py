from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import get_db
from app.services import service
from app.models.schemas import TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Email ve sifre ile giris yap, JWT token al.

    Test kullanicilari (sifre: password123):
    - host@example.com (host rolu)
    - guest@example.com (guest rolu)
    - admin@example.com (admin rolu)
    """
    return service.login(db, form_data.username, form_data.password)

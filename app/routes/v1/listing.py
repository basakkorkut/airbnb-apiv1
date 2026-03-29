from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.config import get_db
from app.auth.jwt_bearer import get_current_user
from app.services import service
from app.models.schemas import ListingCreate, ListingResponse
from datetime import date

router = APIRouter(prefix="/api/v1/listings", tags=["Listings"])


@router.post("/", response_model=ListingResponse, status_code=201)
async def insert_listing(
    listing: ListingCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [Host] Yeni listing olustur.
    Requires: host rolu + JWT token
    """
    return service.create_listing(db, listing, user["user_id"], user["role"])


@router.get("/")
async def query_listings(
    date_from: date = Query(..., description="Giris tarihi"),
    date_to: date = Query(..., description="Cikis tarihi"),
    no_of_people: int = Query(..., gt=0, description="Kisi sayisi"),
    country: str = Query(..., description="Ulke"),
    city: str = Query(..., description="Sehir"),
    page: int = Query(1, ge=1, description="Sayfa numarasi"),
    size: int = Query(10, ge=1, le=50, description="Sayfa boyutu"),
    db: Session = Depends(get_db),
):
    """
    [Guest] Musait listingleri ara.
    Authentication gerektirmez, sayfalama vardir.
    Rate limit: Gunluk 3 cagri (API Gateway'de uygulanir)
    """
    return service.query_listings(
        db, country, city, no_of_people, date_from, date_to, page, size
    )


@router.get("/report")
async def report_listings(
    country: str = Query(..., description="Ulke"),
    city: str = Query(..., description="Sehir"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [Admin] Rating'e gore listing raporu.
    Requires: admin rolu + JWT token + sayfalama
    """
    return service.get_listings_report(
        db, country, city, page, size, user["role"]
    )


@router.post("/upload-csv")
async def insert_listing_by_file(
    file: UploadFile = File(..., description="CSV dosyasi"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [Admin] CSV dosyasindan toplu listing ekle.
    CSV formati: no_of_people,country,city,price,title
    Requires: admin rolu + JWT token
    """
    content = await file.read()
    return service.create_listings_from_csv(
        db, content.decode("utf-8"), user["user_id"], user["role"]
    )

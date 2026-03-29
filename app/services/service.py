from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.repositories import repo
from app.auth.jwt_handler import create_access_token
import csv
import io
import math


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== AUTH SERVICE ====================

def login(db: Session, email: str, password: str):
    """
    1. Email ile kullaniciyi bul
    2. Sifreyi kontrol et
    3. JWT token uret ve don
    """
    user = repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Token icine user_id ve role gom
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })
    return {"access_token": token, "token_type": "bearer"}


# ==================== LISTING SERVICE ====================

def create_listing(db: Session, listing_data, host_id: int, user_role: str):
    """
    KURAL: Sadece host rolundeki kullanici listing olusturabilir
    """
    if user_role != "host":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can create listings"
        )
    return repo.create_listing(db, listing_data, host_id)


def query_listings(db: Session, country: str, city: str, no_of_people: int,
                   date_from, date_to, page: int, size: int = 10):
    """
    Musait listingleri getirir (sayfalanmis).
    KURAL: Rezerve edilmis tarihlerdeki listingler gelmez.
    """
    items, total = repo.query_listings(
        db, country, city, no_of_people, date_from, date_to, page, size
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0,
    }


def create_listings_from_csv(db: Session, file_content: str, host_id: int, user_role: str):
    """
    CSV dosyasindan toplu listing ekleme.
    KURAL: Sadece admin yapabilir.
    CSV formati: no_of_people,country,city,price,title
    """
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload CSV files"
        )

    reader = csv.DictReader(io.StringIO(file_content))
    rows = list(reader)

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty"
        )

    listings = repo.create_listings_bulk(db, rows, host_id)
    return {"status": "success", "created_count": len(listings)}


# ==================== BOOKING SERVICE ====================

def create_booking(db: Session, booking_data, guest_id: int):
    """
    KURAL 1: Listing var mi?
    KURAL 2: Tarih cakismasi var mi?
    KURAL 3: date_to > date_from mi?
    """
    # Listing var mi?
    listing = repo.get_listing_by_id(db, booking_data.listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    # Tarih kontrolu
    if booking_data.date_to <= booking_data.date_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_to must be after date_from"
        )

    # Tarih cakismasi?
    conflict = repo.check_date_conflict(
        db, booking_data.listing_id,
        booking_data.date_from, booking_data.date_to
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Listing is already booked for these dates"
        )

    return repo.create_booking(db, booking_data, guest_id)


# ==================== REVIEW SERVICE ====================

def create_review(db: Session, review_data, reviewer_id: int):
    """
    KURAL 1: Booking var mi?
    KURAL 2: Bu booking'i yapan kisi mi yorum yapiyor?
    KURAL 3: Daha once yorum yapilmis mi?
    """
    # Booking var mi?
    booking = repo.get_booking_by_id(db, review_data.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Bu kisi mi reserve etmis?
    if booking.guest_id != reviewer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the guest who booked can review"
        )

    # Zaten yorum var mi?
    existing = repo.get_review_by_booking_id(db, review_data.booking_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already exists for this booking"
        )

    return repo.create_review(db, review_data, reviewer_id)


# ==================== REPORT SERVICE ====================

def get_listings_report(db: Session, country: str, city: str,
                        page: int, size: int, user_role: str):
    """
    KURAL: Sadece admin gorebilir.
    """
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view reports"
        )

    items, total = repo.get_listings_with_ratings(db, country, city, page, size)

    report_items = []
    for item in items:
        report_items.append({
            "id": item.id,
            "title": item.title,
            "country": item.country,
            "city": item.city,
            "price": item.price,
            "avg_rating": round(float(item.avg_rating), 1) if item.avg_rating else None,
            "review_count": item.review_count,
        })

    return {
        "items": report_items,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0,
    }

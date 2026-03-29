from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import User, Listing, Booking, Review
from datetime import date


# ==================== USER REPO ====================

def get_user_by_email(db: Session, email: str):
    """SELECT * FROM users WHERE email = ?"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """SELECT * FROM users WHERE id = ?"""
    return db.query(User).filter(User.id == user_id).first()


# ==================== LISTING REPO ====================

def create_listing(db: Session, listing_data, host_id: int):
    """INSERT INTO listings (...)"""
    new_listing = Listing(
        host_id=host_id,
        title=listing_data.title,
        no_of_people=listing_data.no_of_people,
        country=listing_data.country,
        city=listing_data.city,
        price=listing_data.price,
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

def get_listing_by_id(db: Session, listing_id: int):
    """SELECT * FROM listings WHERE id = ?"""
    return db.query(Listing).filter(Listing.id == listing_id).first()

def query_listings(db: Session, country: str, city: str, no_of_people: int,
                   date_from: date, date_to: date, page: int, size: int):
    """
    Musait listingleri getirir.
    - Ulke ve sehir filtresi
    - Kisi sayisi filtresi
    - Tarih cakismasi olanlari HARIC tutar
    - Sayfalama uygular
    """
    # Tarih cakismasi olan booking'lerin listing_id'lerini bul
    booked_ids = db.query(Booking.listing_id).filter(
        Booking.date_from < date_to,
        Booking.date_to > date_from,
        Booking.status == "confirmed"
    ).subquery()

    # Filtreleri uygula, cakisan listingleri cikar
    query = db.query(Listing).filter(
        Listing.country == country,
        Listing.city == city,
        Listing.no_of_people >= no_of_people,
        Listing.id.notin_(booked_ids)
    )

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return items, total

def create_listings_bulk(db: Session, listings_data: list, host_id: int):
    """CSV'den toplu listing ekleme"""
    new_listings = []
    for data in listings_data:
        listing = Listing(
            host_id=host_id,
            title=data.get("title", "Unnamed Listing"),
            no_of_people=int(data["no_of_people"]),
            country=data["country"],
            city=data["city"],
            price=float(data["price"]),
        )
        db.add(listing)
        new_listings.append(listing)
    db.commit()
    for l in new_listings:
        db.refresh(l)
    return new_listings


# ==================== BOOKING REPO ====================

def create_booking(db: Session, booking_data, guest_id: int):
    """INSERT INTO bookings (...)"""
    new_booking = Booking(
        listing_id=booking_data.listing_id,
        guest_id=guest_id,
        date_from=booking_data.date_from,
        date_to=booking_data.date_to,
        guest_names=booking_data.guest_names,
        status="confirmed",
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

def check_date_conflict(db: Session, listing_id: int, date_from: date, date_to: date):
    """Tarih cakismasi kontrolu"""
    return db.query(Booking).filter(
        Booking.listing_id == listing_id,
        Booking.date_from < date_to,
        Booking.date_to > date_from,
        Booking.status == "confirmed"
    ).first()

def get_booking_by_id(db: Session, booking_id: int):
    """SELECT * FROM bookings WHERE id = ?"""
    return db.query(Booking).filter(Booking.id == booking_id).first()


# ==================== REVIEW REPO ====================

def create_review(db: Session, review_data, reviewer_id: int):
    """INSERT INTO reviews (...)"""
    new_review = Review(
        booking_id=review_data.booking_id,
        reviewer_id=reviewer_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

def get_review_by_booking_id(db: Session, booking_id: int):
    """Bu booking icin zaten review var mi?"""
    return db.query(Review).filter(Review.booking_id == booking_id).first()

def get_listings_with_ratings(db: Session, country: str, city: str, page: int, size: int):
    """
    Admin raporu: Listing + ortalama rating
    LEFT JOIN ile review'suz listingleri de getirir
    """
    query = db.query(
        Listing.id,
        Listing.title,
        Listing.country,
        Listing.city,
        Listing.price,
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("review_count"),
    ).outerjoin(
        Booking, Listing.id == Booking.listing_id
    ).outerjoin(
        Review, Booking.id == Review.booking_id
    ).filter(
        Listing.country == country,
        Listing.city == city,
    ).group_by(Listing.id)

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return items, total

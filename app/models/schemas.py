from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


# ==================== AUTH ====================

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==================== LISTING ====================

class ListingCreate(BaseModel):
    """Host'un gonderdigi veri (input DTO)"""
    no_of_people: int = Field(gt=0, description="Kac kisi kalabilir")
    country: str = Field(min_length=1)
    city: str = Field(min_length=1)
    price: float = Field(gt=0)
    title: Optional[str] = "Unnamed Listing"

class ListingResponse(BaseModel):
    """Kullaniciya donen veri (output DTO)"""
    id: int
    host_id: int
    title: str
    no_of_people: int
    country: str
    city: str
    price: float

    class Config:
        from_attributes = True  # SQLAlchemy obj -> Pydantic obj


class ListingQueryParams(BaseModel):
    """Query Listings icin filtre parametreleri"""
    date_from: date
    date_to: date
    no_of_people: int = Field(gt=0)
    country: str
    city: str


# ==================== BOOKING ====================

class BookingCreate(BaseModel):
    """Guest'in gonderdigi veri"""
    listing_id: int
    date_from: date
    date_to: date
    guest_names: str = Field(min_length=1, description="Virgul ile ayrilmis isimler")

class BookingResponse(BaseModel):
    id: int
    listing_id: int
    guest_id: int
    date_from: date
    date_to: date
    guest_names: str
    status: str

    class Config:
        from_attributes = True


# ==================== REVIEW ====================

class ReviewCreate(BaseModel):
    """Guest'in gonderdigi yorum"""
    booking_id: int
    rating: int = Field(ge=1, le=5, description="1-5 arasi puan")
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    reviewer_id: int
    rating: int
    comment: Optional[str]

    class Config:
        from_attributes = True


# ==================== REPORT ====================

class ListingReportItem(BaseModel):
    """Admin raporunda her bir listing"""
    id: int
    title: str
    country: str
    city: str
    price: float
    avg_rating: Optional[float] = None
    review_count: int = 0

    class Config:
        from_attributes = True


# ==================== PAGINATION ====================

class PaginatedResponse(BaseModel):
    """Sayfalanmis cevap wrapper"""
    items: list
    total: int
    page: int
    size: int
    pages: int

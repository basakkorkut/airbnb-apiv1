from app.gateway import APIGatewayMiddleware
from fastapi import FastAPI
from app.routes.v1 import auth, listing, booking, review

app = FastAPI(
    title="Short-Term Stay API",
    description="""
   Short-term accommodation API.

**Roles:**
- Host: Can create listings
- Guest: Can search listings, make reservations, and leave reviews
- Admin: Can view reports and upload CSV files

**Test users** (password: password123):
    **Test kullanicilari** (sifre: password123):
    - host@example.com | guest@example.com | admin@example.com
    """,
    version="1.0.0",
)
app.add_middleware(APIGatewayMiddleware)
# Route'lari kaydet
app.include_router(auth.router)
app.include_router(listing.router)
app.include_router(booking.router)
app.include_router(review.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Short-Term Stay API is running"}

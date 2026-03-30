# Overview

Short-Term Stay API is a simplified Airbnb-style backend that supports:

- Authentication via JWT (Bearer tokens)
- Role-based capabilities:
  - `host`: create listings
  - `guest`: search listings, book stays, write reviews
  - `admin`: upload listings via CSV and view reporting endpoints
- Availability search with booking overlap exclusion
- Booking creation with conflict detection
- One-review-per-booking enforcement
- Basic API-gateway-style middleware for request logging and rate limiting

## Tech Stack

- **Web framework**: FastAPI
- **ASGI server**: Uvicorn (development) / Gunicorn + UvicornWorker (production)
- **ORM**: SQLAlchemy (declarative models)
- **Database driver**: psycopg (PostgreSQL)
- **Auth**: OAuth2 Password flow (login) + JWT validation
- **Validation**: Pydantic v2

## Project Structure

All application code lives under [app/](file:///Users/basakkorkut/Desktop/airbnb-api/app):

- [main.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/main.py): FastAPI application creation and router registration
- [gateway.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/gateway.py): middleware for logging and rate limiting
- [config.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/config.py): environment + SQLAlchemy engine/session dependency
- [routes/v1/](file:///Users/basakkorkut/Desktop/airbnb-api/app/routes/v1): HTTP endpoints grouped by domain
- [services/](file:///Users/basakkorkut/Desktop/airbnb-api/app/services): business rules and validation beyond Pydantic
- [repositories/](file:///Users/basakkorkut/Desktop/airbnb-api/app/repositories): SQLAlchemy queries and persistence
- [models/](file:///Users/basakkorkut/Desktop/airbnb-api/app/models): SQLAlchemy models + Pydantic schemas
- [auth/](file:///Users/basakkorkut/Desktop/airbnb-api/app/auth): JWT creation/verification helpers

## Key Runtime Entry Points

- ASGI app: `app.main:app` ([main.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/main.py))
- Production start command: [startup.sh](file:///Users/basakkorkut/Desktop/airbnb-api/startup.sh)

## What Is Not Included

- No migration tooling is present (e.g., Alembic).
- No automated database initialization/seed scripts are included in this repository.

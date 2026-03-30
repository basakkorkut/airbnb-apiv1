# Architecture

## Layering

The code is organized as a classic layered API:

1. **Routes (HTTP layer)**: parse inputs, declare dependencies, return outputs  
   Source: [routes/v1/](file:///Users/basakkorkut/Desktop/airbnb-api/app/routes/v1)
2. **Services (business layer)**: enforce business rules, map errors to HTTP exceptions  
   Source: [service.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/services/service.py)
3. **Repositories (persistence layer)**: SQLAlchemy queries and commits  
   Source: [repo.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/repositories/repo.py)
4. **Models/Schemas**:
   - SQLAlchemy entities: [models.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/models/models.py)
   - Pydantic DTOs: [schemas.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/models/schemas.py)

This separation keeps HTTP concerns (FastAPI) out of database query logic, and concentrates business rules in a single location.

## Request Flow

For a typical authenticated request:

1. FastAPI receives the request (ASGI app: [main.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/main.py)).
2. Middleware runs first ([gateway.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/gateway.py)):
   - Logs method/path/status/duration
   - Applies a daily rate limit to `GET /api/v1/listings/`
3. Route handler runs and resolves dependencies:
   - `db: Session = Depends(get_db)` yields a SQLAlchemy session ([config.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/config.py#L20-L25))
   - `user = Depends(get_current_user)` decodes the JWT and returns `{user_id, role}` ([jwt_bearer.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/auth/jwt_bearer.py#L16-L44))
4. Service function applies business rules and delegates to repository functions.
5. Repository persists or reads entities and returns SQLAlchemy objects.
6. FastAPI serializes responses; where response models are defined, Pydantic’s `from_attributes` converts ORM objects into DTOs.

## Authentication & Authorization

### Login (Token Issuance)

- Endpoint: `POST /api/v1/auth/login` ([auth.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/routes/v1/auth.py))
- Flow:
  - Look up user by email
  - Verify password via bcrypt (`passlib`)
  - Create a JWT containing:
    - `sub`: user id (string)
    - `role`: authorization role
    - `exp`: expiry
  - Return `{access_token, token_type}`
  Source: [service.login](file:///Users/basakkorkut/Desktop/airbnb-api/app/services/service.py#L16-L41), [create_access_token](file:///Users/basakkorkut/Desktop/airbnb-api/app/auth/jwt_handler.py#L13-L25)

### Token Verification (Per Request)

- Dependency: [get_current_user](file:///Users/basakkorkut/Desktop/airbnb-api/app/auth/jwt_bearer.py#L16-L44)
- Responsibilities:
  - Read Bearer token from `Authorization` header
  - Decode JWT using `SECRET_KEY` and `ALGORITHM`
  - Return `user_id` and `role`, or raise `401`

### Role Enforcement

Role checks are enforced in the service layer:

- Only `host` can create listings: [create_listing](file:///Users/basakkorkut/Desktop/airbnb-api/app/services/service.py#L45-L55)
- Only `admin` can upload CSV listings: [create_listings_from_csv](file:///Users/basakkorkut/Desktop/airbnb-api/app/services/service.py#L75-L98)
- Only `admin` can view reports: [get_listings_report](file:///Users/basakkorkut/Desktop/airbnb-api/app/services/service.py#L173-L204)

## Rate Limiting

Middleware applies a per-IP, per-day in-memory rate limit:

- Applies only to: `GET /api/v1/listings/`
- Limit: 3 requests per day per IP
- On exceed: returns `429` with a JSON error body
- Adds headers on successful responses:
  - `X-RateLimit-Limit: 3`
  - `X-RateLimit-Remaining: <0..3>`

Source: [APIGatewayMiddleware](file:///Users/basakkorkut/Desktop/airbnb-api/app/gateway.py#L8-L57)

## Booking Availability Logic

Listing search excludes listings with overlapping confirmed bookings:

- Overlap condition:
  - `Booking.date_from < date_to` AND `Booking.date_to > date_from`
  - and `Booking.status == "confirmed"`
- Excludes conflicting listing IDs via a subquery

Source: [repo.query_listings](file:///Users/basakkorkut/Desktop/airbnb-api/app/repositories/repo.py#L39-L67)

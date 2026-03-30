# API Reference

Base path: `/api/v1`

Interactive API docs are available when the app is running:

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## Authentication

### POST `/auth/login`

Logs in a user and returns a JWT access token.

- Content-Type: `application/x-www-form-urlencoded` (OAuth2 password flow)
- Form fields:
  - `username`: user email
  - `password`: user password

Response (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Error responses:

- `401 Unauthorized`: invalid email or password

Example:

```bash
curl -s -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=password&username=guest%40example.com&password=password123'
```

## Listings

### POST `/listings/` (Host only)

Creates a listing owned by the authenticated host.

Auth: `Authorization: Bearer <token>`

Request body:

```json
{
  "no_of_people": 2,
  "country": "Turkey",
  "city": "Istanbul",
  "price": 120.0,
  "title": "Central flat"
}
```

Response (201):

```json
{
  "id": 1,
  "host_id": 10,
  "title": "Central flat",
  "no_of_people": 2,
  "country": "Turkey",
  "city": "Istanbul",
  "price": 120.0
}
```

Error responses:

- `401 Unauthorized`: missing/invalid token
- `403 Forbidden`: user role is not `host`

### GET `/listings/` (Public, rate limited)

Searches for available listings in a city/country for a date range.

Auth: not required  
Rate limit: 3 requests/day/IP (middleware-enforced). On successful responses, the API returns:

- `X-RateLimit-Limit: 3`
- `X-RateLimit-Remaining: <0..3>`

Query parameters:

- `date_from` (date, required): check-in date
- `date_to` (date, required): check-out date
- `no_of_people` (int, required, > 0)
- `country` (string, required)
- `city` (string, required)
- `page` (int, default 1, >= 1)
- `size` (int, default 10, 1..50)

Response (200):

```json
{
  "items": [
    {
      "id": 1,
      "host_id": 10,
      "title": "Central flat",
      "no_of_people": 2,
      "country": "Turkey",
      "city": "Istanbul",
      "price": 120.0
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

Error responses:

- `429 Too Many Requests`: daily limit exceeded

Example:

```bash
curl -s 'http://localhost:8000/api/v1/listings/?date_from=2026-07-01&date_to=2026-07-05&no_of_people=2&country=Turkey&city=Istanbul&page=1&size=10'
```

### GET `/listings/report` (Admin only)

Returns listings with aggregated rating metrics.

Auth: required, role must be `admin`

Query parameters:

- `country` (string, required)
- `city` (string, required)
- `page` (int, default 1, >= 1)
- `size` (int, default 10, 1..50)

Response (200):

```json
{
  "items": [
    {
      "id": 1,
      "title": "Central flat",
      "country": "Turkey",
      "city": "Istanbul",
      "price": 120.0,
      "avg_rating": 4.5,
      "review_count": 2
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

Error responses:

- `401 Unauthorized`: missing/invalid token
- `403 Forbidden`: user role is not `admin`

### POST `/listings/upload-csv` (Admin only)

Creates listings in bulk from a CSV file.

Auth: required, role must be `admin`

Multipart form-data:

- `file`: CSV file

CSV format (header row required):

```
no_of_people,country,city,price,title
2,Turkey,Istanbul,120,Central flat
```

Response (200):

```json
{
  "status": "success",
  "created_count": 10
}
```

Error responses:

- `401 Unauthorized`: missing/invalid token
- `403 Forbidden`: user role is not `admin`
- `400 Bad Request`: empty CSV file

## Bookings

### POST `/bookings/` (Authenticated)

Creates a confirmed booking for a listing.

Auth: required (any logged-in user can call it; business rules assume “guest behavior”)

Request body:

```json
{
  "listing_id": 1,
  "date_from": "2027-01-01",
  "date_to": "2027-01-05",
  "guest_names": "Alice,Bob"
}
```

Response (201):

```json
{
  "id": 100,
  "listing_id": 1,
  "guest_id": 20,
  "date_from": "2027-01-01",
  "date_to": "2027-01-05",
  "guest_names": "Alice,Bob",
  "status": "confirmed"
}
```

Error responses:

- `401 Unauthorized`: missing/invalid token
- `404 Not Found`: listing does not exist
- `400 Bad Request`: `date_to` is not after `date_from`
- `409 Conflict`: listing is already booked for the given date range

## Reviews

### POST `/reviews/` (Authenticated)

Creates a review for a booking. Only the booking’s guest can review, and only one review per booking is allowed.

Auth: required

Request body:

```json
{
  "booking_id": 100,
  "rating": 5,
  "comment": "Great stay!"
}
```

Response (201):

```json
{
  "id": 55,
  "booking_id": 100,
  "reviewer_id": 20,
  "rating": 5,
  "comment": "Great stay!"
}
```

Error responses:

- `401 Unauthorized`: missing/invalid token
- `404 Not Found`: booking does not exist
- `403 Forbidden`: booking belongs to a different guest
- `409 Conflict`: a review already exists for this booking

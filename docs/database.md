# Database & ER Diagram

This project uses SQLAlchemy to map a small relational schema intended for an Airbnb-like short-term stay domain.

## Entities

### `users`

Represents application users. Authorization decisions are driven by the `role` field embedded into JWTs at login time.

- `id` (int, PK)
- `email` (varchar(255), unique, not null)
- `password_hash` (varchar(255), not null)
- `full_name` (varchar(255), not null)
- `role` (varchar(20), not null, default: `guest`)  
  Expected values in the codebase: `guest`, `host`, `admin`
- `created_at` (timestamp with tz, default: now)

### `listings`

Represents properties published by hosts.

- `id` (int, PK)
- `host_id` (int, FK → `users.id`, not null, on delete: cascade)
- `title` (varchar(255), not null, default: `Unnamed Listing`)
- `no_of_people` (int, not null)
- `country` (varchar(100), not null)
- `city` (varchar(100), not null)
- `price` (float, not null)
- `created_at` (timestamp with tz, default: now)

### `bookings`

Represents a reservation made by a guest for a listing.

- `id` (int, PK)
- `listing_id` (int, FK → `listings.id`, not null, on delete: cascade)
- `guest_id` (int, FK → `users.id`, not null, on delete: cascade)
- `date_from` (date, not null)
- `date_to` (date, not null)
- `guest_names` (text, not null)  
  Business meaning: a comma-separated list of guest names.
- `status` (varchar(20), not null, default: `confirmed`)
- `created_at` (timestamp with tz, default: now)

### `reviews`

Represents a review attached to a booking. The schema enforces “one review per booking” by a unique constraint on `booking_id`.

- `id` (int, PK)
- `booking_id` (int, FK → `bookings.id`, not null, unique, on delete: cascade)
- `reviewer_id` (int, FK → `users.id`, not null, on delete: cascade)
- `rating` (int, not null)  
  API-level validation enforces 1..5.
- `comment` (text, nullable)
- `created_at` (timestamp with tz, default: now)

## Relationships (Cardinality)

- A `User` (host) has many `Listing`s (`users.id` → `listings.host_id`).
- A `User` (guest) has many `Booking`s (`users.id` → `bookings.guest_id`).
- A `Listing` has many `Booking`s (`listings.id` → `bookings.listing_id`).
- A `Booking` has zero or one `Review` (`bookings.id` → `reviews.booking_id`, unique).
- A `User` (reviewer) can have many `Review`s (`users.id` → `reviews.reviewer_id`).

## Mermaid ER Diagram

```mermaid
erDiagram
  USERS ||--o{ LISTINGS : hosts
  USERS ||--o{ BOOKINGS : makes
  LISTINGS ||--o{ BOOKINGS : contains
  BOOKINGS ||--o| REVIEWS : has
  USERS ||--o{ REVIEWS : writes

  USERS {
    int id PK
    varchar email UK
    varchar password_hash
    varchar full_name
    varchar role
    datetime created_at
  }

  LISTINGS {
    int id PK
    int host_id FK
    varchar title
    int no_of_people
    varchar country
    varchar city
    float price
    datetime created_at
  }

  BOOKINGS {
    int id PK
    int listing_id FK
    int guest_id FK
    date date_from
    date date_to
    text guest_names
    varchar status
    datetime created_at
  }

  REVIEWS {
    int id PK
    int booking_id FK UK
    int reviewer_id FK
    int rating
    text comment
    datetime created_at
  }
```

## Notes & Gaps

- There is no migration tool (e.g., Alembic) included in the repository; schema lifecycle (create/update) is not automated here.
- Several business constraints are enforced at the API/service layer instead of the database:
  - `date_to` must be after `date_from`
  - booking overlap prevention for `confirmed` bookings
  - rating range 1..5 (Pydantic validation)

# Short-Term Stay API

REST API for a short-term accommodation platform similar to Airbnb.  
**SE4458 Software Architecture & Design of Modern Large Scale Systems - Midterm Project**

**Student:** Başak Nur Korkut  
**Deployed Swagger:** [https://airbnb-apiv1-f7a7aedkcyfcbaba.italynorth-01.azurewebsites.net/docs](https://airbnb-apiv1-f7a7aedkcyfcbaba.italynorth-01.azurewebsites.net/docs)  
**Video:** https://drive.google.com/file/d/1hEcmu2gKoAkyN4mMjfKHm2CO2taSeD9e/view?usp=sharing

---

## Technology Stack

- **Backend:** Python FastAPI
- **Database:** PostgreSQL (Supabase - cloud hosted)
- **ORM:** SQLAlchemy
- **Authentication:** JWT (python-jose + passlib/bcrypt)
- **Deployment:** Azure App Service (Free F1 tier)
- **CI/CD:** GitHub Actions
- **Load Testing:** k6

---

## Architecture

The project follows a **service-oriented architecture** with three distinct layers:

```
Client (Swagger UI)
    ↓
API Gateway (rate limiting, logging)
    ↓
Routes/Controllers (HTTP handling only)
    ↓
Services (business logic, validation)
    ↓
Repositories (database operations only)
    ↓
PostgreSQL (Supabase)
```

- **Routes** only handle HTTP request/response. No business logic or database operations.
- **Services** enforce business rules (date conflicts, role checks, review ownership).
- **Repositories** perform database CRUD operations only. No business rules.
- **DTOs (Pydantic schemas)** define input/output data shapes with automatic validation.

---

## Data Model

```
┌──────────────┐       ┌──────────────┐
│    USERS     │       │   LISTINGS   │
├──────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)      │
│ email        │  │    │ host_id (FK) │──┐
│ password_hash│  │    │ title        │  │
│ full_name    │  │    │ no_of_people │  │
│ role         │  │    │ country      │  │
│ created_at   │  │    │ city         │  │
└──────────────┘  │    │ price        │  │
                  │    │ created_at   │  │
                  │    └──────────────┘  │
                  │                      │
                  │    ┌──────────────┐  │
                  │    │   BOOKINGS   │  │
                  │    ├──────────────┤  │
                  ├───>│ id (PK)      │  │
                  │    │ listing_id(FK)│<─┘
                  │    │ guest_id (FK)│
                  │    │ date_from    │
                  │    │ date_to      │
                  │    │ guest_names  │
                  │    │ status       │
                  │    │ created_at   │
                  │    └──────────────┘
                  │           │
                  │    ┌──────────────┐
                  │    │   REVIEWS    │
                  │    ├──────────────┤
                  └───>│ id (PK)      │
                       │ booking_id(FK)│ (UNIQUE)
                       │ reviewer_id  │
                       │ rating (1-5) │
                       │ comment      │
                       │ created_at   │
                       └──────────────┘
```

**Relationships:**
- A User (host) can create many Listings (1:N)
- A User (guest) can make many Bookings (1:N)
- A Listing can have many Bookings (1:N)
- A Booking can have at most one Review (1:1)

---

## API Endpoints

| Endpoint | Method | Auth | Paging | Role | Description |
|----------|--------|------|--------|------|-------------|
| `/api/v1/auth/login` | POST | No | No | All | Login and get JWT token |
| `/api/v1/listings/` | POST | JWT | No | Host | Create a new listing |
| `/api/v1/listings/` | GET | No | Yes (10) | All | Search available listings |
| `/api/v1/listings/report` | GET | JWT | Yes (10) | Admin | Listings report with ratings |
| `/api/v1/listings/upload-csv` | POST | JWT | No | Admin | Bulk create listings from CSV |
| `/api/v1/bookings/` | POST | JWT | No | All | Book a stay |
| `/api/v1/reviews/` | POST | JWT | No | All | Review a stay |

### Authentication & Authorization

- JWT tokens are issued on login with user ID and role embedded in the payload.
- Tokens expire after 30 minutes.
- Role-based access control: Host can create listings, Admin can view reports and upload CSV, Guest can search/book/review.

### Rate Limiting

- Query Listings endpoint is limited to **3 calls per day** per IP address.
- Implemented via API Gateway middleware.
- Returns `429 Too Many Requests` when limit is exceeded.
- `X-RateLimit-Remaining` header shows remaining calls.

### Paging

- Query Listings and Report Listings support pagination.
- Default page size: 10
- Parameters: `page` (page number), `size` (items per page)

---

## Assumptions

1. User registration is not required — test users are pre-seeded in the database.
2. No payment processing is needed for bookings (as stated in requirements).
3. Rate limiting is IP-based and resets daily.
4. CSV upload format: `no_of_people,country,city,price,title`
5. A listing that is booked for certain dates will not appear in query results for overlapping dates.
6. Only the guest who made a booking can review it, and each booking can only be reviewed once.

---

## Issues Encountered

1. **psycopg2 installation on Mac:** The `psycopg2-binary` package failed to compile on macOS. Resolved by switching to `psycopg[binary]` (psycopg3).
2. **Supabase connection:** Direct database connection (`db.xxx.supabase.co`) was not resolvable. Resolved by using Supabase's connection pooler (`aws-1-eu-central-1.pooler.supabase.com`).
3. **bcrypt version incompatibility:** New bcrypt 5.x was incompatible with passlib. Resolved by pinning `bcrypt==4.0.1`.
4. **Azure deployment region:** Azure for Students subscription had quota restrictions in some European regions. Resolved by selecting Italy North region.
5. **Password hash mismatch:** Pre-seeded bcrypt hashes were incompatible with the installed bcrypt version. Resolved by regenerating hashes with the correct bcrypt version.

---

## Load Test Results

Load testing was performed using **k6** on the deployed Azure endpoint.  
Two endpoints were tested: **Query Listings** (GET) and **Book a Stay** (POST).  
Each test ran for **30 seconds**.

### Results Summary

| Metric | Normal (20 VUs) | Peak (50 VUs) | Stress (100 VUs) |
|--------|-----------------|---------------|-------------------|
| Avg response time | 944 ms | 9.11 s | 13.29 s |
| p95 response time | 2.41 s | 27.46 s | 30.18 s |
| Requests/sec | 9.64 | 2.60 | 6.65 |
| Total requests | 321 | 158 | 401 |
| Error rate | 96.88% | 97.46% | 98.25% |

### Analysis

Under normal load (20 VUs), the API showed acceptable performance with an average response time of 944ms. As load increased to 50 and 100 virtual users, response times rose dramatically — p95 reached 30 seconds. The main bottleneck is Azure Free (F1) tier's limited CPU and memory resources (1 GB RAM, shared infrastructure), along with Supabase free plan's connection pool limits. The Book a Stay endpoint was more affected under load because it requires database write operations with conflict checks. To improve scalability: upgrade to higher Azure tiers (B1/S1), optimize connection pooling, implement caching for read-heavy endpoints, and consider database read replicas.

### Test Script

The k6 test script is located at: `load_test.js`

---

## How to Run Locally

```bash
# Clone the repository
git clone https://github.com/basakkorkut/airbnb-apiv1.git
cd airbnb-apiv1

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
# DATABASE_URL=postgresql+psycopg://...
# SECRET_KEY=your-secret-key
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# Run the application
uvicorn app.main:app --reload

# Open Swagger UI
# http://localhost:8000/docs
```

### Test Users (password: password123)
- `host@example.com` — Host role (can create listings)
- `guest@example.com` — Guest role (can search, book, review)
- `admin@example.com` — Admin role (can view reports, upload CSV)

---

## Project Structure

```
airbnb-apiv1/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Database configuration (SQLAlchemy + Supabase)
│   ├── gateway.py            # API Gateway middleware (rate limiting, logging)
│   ├── auth/
│   │   ├── jwt_handler.py    # JWT token creation
│   │   └── jwt_bearer.py     # JWT token validation (dependency)
│   ├── models/
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   └── schemas.py        # Pydantic DTOs
│   ├── routes/v1/
│   │   ├── auth.py           # Login endpoint
│   │   ├── listing.py        # Listing CRUD + query + report + CSV
│   │   ├── booking.py        # Booking endpoint
│   │   └── review.py         # Review endpoint
│   ├── services/
│   │   └── service.py        # Business logic
│   └── repositories/
│       └── repo.py           # Database operations
├── load_test.js              # k6 load test script
├── startup.sh                # Azure startup command
├── requirements.txt          # Python dependencies
└── README.md
```
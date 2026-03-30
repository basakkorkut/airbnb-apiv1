# Configuration & Running Locally

## Prerequisites

- Python 3.10+ (the CI workflow uses Python 3.13)
- A database reachable via `DATABASE_URL` (PostgreSQL is the intended target)

## Environment Variables

The application reads configuration from environment variables (and `.env` if present).

- `DATABASE_URL` (required)  
  Example (PostgreSQL):
  - `postgresql://USER:PASSWORD@HOST:5432/DBNAME`
  The application rewrites this to `postgresql+psycopg://...` internally.

- `SECRET_KEY` (recommended)  
  JWT signing secret. If unset, a default value is used; do not rely on the default in real deployments.

- `ALGORITHM` (optional, default `HS256`)  
  JWT signing algorithm.

- `ACCESS_TOKEN_EXPIRE_MINUTES` (optional, default `30`)  
  JWT expiry duration.

Source: [config.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/config.py), [jwt_handler.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/auth/jwt_handler.py)

## Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run in Development

```bash
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- `http://localhost:8000/` (health)
- `http://localhost:8000/docs` (Swagger UI)

## Run in Production Mode

The repository includes a production startup script:

- [startup.sh](file:///Users/basakkorkut/Desktop/airbnb-api/startup.sh)

```bash
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME'
./startup.sh
```

## Database Initialization

This repository does not include migrations or table creation scripts (no Alembic, and no `Base.metadata.create_all(...)` call).

To use the API end-to-end, you must ensure the schema exists in your database matching the SQLAlchemy models in:

- [models.py](file:///Users/basakkorkut/Desktop/airbnb-api/app/models/models.py)

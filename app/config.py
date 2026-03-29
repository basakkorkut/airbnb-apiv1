import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine - Supabase'e baglanir
engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg://"), pool_pre_ping=True)

# Session factory - her request icin bir session olusturur
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class - tum modeller bundan turetilir
Base = declarative_base()


def get_db():
    """
    FastAPI dependency - her istekte yeni DB session acilir,
    istek bitince otomatik kapatilir.
    
    Kullanim:
        @router.get("/")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

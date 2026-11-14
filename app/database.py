import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Load environment variables from .env
load_dotenv()


# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Check required configuration
if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Database environment variables are missing.")


# Create database URL safely
from sqlalchemy.engine import URL

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for database models
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# For Railway deployment, the DATABASE_URL might need adjustment
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    if SessionLocal is None:
        raise Exception("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
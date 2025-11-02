from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configure engine with production-optimized settings for Vercel serverless
connect_args = {}
if "supabase.co" in settings.DATABASE_URL:
    # Supabase configuration optimized for serverless
    connect_args = {
        "sslmode": "require",
        "connect_timeout": 15,
        "application_name": "ats-vercel-app"
    }

# Create engine optimized for serverless with minimal pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes  
    pool_size=1,  # Minimal pool for serverless
    max_overflow=0,  # No overflow for serverless
    echo=False,  # Disable SQL logging in production
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

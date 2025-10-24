from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.config import settings
from app.db.database import engine
from app.db import models
import logging

logger = logging.getLogger(__name__)

# Create database tables (commented out - run migrations script instead)
# Note: Database must exist before running this application
# Run: python backend/create_database.py to create the database
# Run: python backend/create_tables.py to create all tables
try:
    # Debug: show which DATABASE_URL is being used at startup
    logger.info(f"Database URL at startup: {settings.DATABASE_URL}")
    models.Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables verified/created successfully")
except Exception as e:
    logger.warning(f"⚠ Could not create tables at startup: {e}")
    logger.warning("Please ensure the database exists and run create_tables.py")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ATS/AI Application - Applicant Tracking System with AI capabilities"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to ATS/AI Application",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

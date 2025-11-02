from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.config import settings
from app.db.database import engine
from app.db import models
import logging

logger = logging.getLogger(__name__)

# Skip table creation in production since tables already exist
# This avoids potential errors during startup
try:
    # Test database connection
    from sqlalchemy import text
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logger.info("✓ Database connection successful")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    # Don't fail startup - let individual requests handle DB errors

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

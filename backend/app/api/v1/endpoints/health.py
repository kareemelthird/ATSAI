from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
        logger.info("✅ Health check: Database connection successful")
    except Exception as e:
        db_status = "error"
        logger.error(f"❌ Health check: Database connection failed: {e}")
    
    return {
        "status": "healthy",
        "database_status": db_status,
        "service": "ATS/AI Application"
    }
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection with a simple query
        result = db.execute(text("SELECT version()"))
        version_info = result.fetchone()
        db_status = "connected"
        db_version = str(version_info[0])[:50] if version_info else "unknown"
        logger.info(f"✅ Health check: Database connection successful - {db_version}")
    except Exception as e:
        db_status = "error"
        db_version = str(e)[:100]
        logger.error(f"❌ Health check: Database connection failed: {e}")
    
    return {
        "status": "healthy",
        "database_status": db_status,
        "database_info": db_version,
        "service": "ATS/AI Application"
    }
    
    return {
        "status": "healthy",
        "database_status": db_status,
        "service": "ATS/AI Application"
    }
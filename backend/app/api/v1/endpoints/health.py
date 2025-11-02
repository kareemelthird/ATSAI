from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, engine
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint with database connectivity test"""
    # Simple backend status
    backend_status = "healthy"
    
    # Database connectivity test with timeout
    try:
        # Create a new connection for testing
        with engine.connect() as connection:
            start_time = time.time()
            result = connection.execute(text("SELECT version()"))
            version_info = result.fetchone()
            connection_time = time.time() - start_time
            
            db_status = "connected"
            db_version = str(version_info[0])[:50] if version_info else "unknown"
            db_info = f"{db_version} (connected in {connection_time:.2f}s)"
            logger.info(f"✅ Health check: Database connection successful - {db_info}")
            
    except Exception as e:
        db_status = "error"
        db_info = str(e)[:100]
        logger.error(f"❌ Health check: Database connection failed: {e}")
    
    return {
        "status": backend_status,
        "database_status": db_status,
        "database_info": db_info,
        "service": "ATS/AI Application"
    }
    
    return {
        "status": "healthy",
        "database_status": db_status,
        "service": "ATS/AI Application"
    }
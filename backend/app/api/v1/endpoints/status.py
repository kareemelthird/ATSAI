"""
System status endpoint for admin overview
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user
from app.db.models_users import User
from app.db import models

router = APIRouter()

@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system status and user permissions"""
    
    # Check if user is admin
    is_admin = current_user.role in ["admin", "super_admin"]
    
    # Get basic counts
    candidate_count = db.query(models.Candidate).count()
    job_count = db.query(models.Job).count()
    application_count = db.query(models.Application).count()
    resume_count = db.query(models.Resume).count()
    user_count = db.query(User).count()
    
    return {
        "user_info": {
            "email": current_user.email,
            "role": current_user.role,
            "status": current_user.status,
            "is_admin": is_admin,
            "can_manage_users": is_admin,
            "can_view_settings": is_admin
        },
        "system_counts": {
            "candidates": candidate_count,
            "jobs": job_count, 
            "applications": application_count,
            "resumes": resume_count,
            "users": user_count
        },
        "features_available": {
            "pdf_upload": True,
            "ai_analysis": True,
            "admin_panel": is_admin,
            "user_management": is_admin
        },
        "recent_activity": {
            "latest_candidate": db.query(models.Candidate).order_by(models.Candidate.created_at.desc()).first().email if candidate_count > 0 else None,
            "latest_resume": db.query(models.Resume).order_by(models.Resume.upload_date.desc()).first().original_filename if resume_count > 0 else None
        }
    }
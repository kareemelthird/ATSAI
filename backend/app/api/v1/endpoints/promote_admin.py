"""
Temporary Admin Promotion Endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.db.models_users import User
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/promote-to-super-admin")
async def promote_admin_to_super_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Temporary endpoint to promote the first admin user to super_admin
    This is a one-time use endpoint for initial setup
    """
    
    # Security check - only allow for admin@ats.com and only if they're currently admin
    if current_user.email != 'admin@ats.com' or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for initial admin promotion"
        )
    
    # Update the user role
    current_user.role = 'super_admin'
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Successfully promoted to Super Admin",
        "user": {
            "email": current_user.email,
            "role": current_user.role,
            "status": current_user.status
        }
    }
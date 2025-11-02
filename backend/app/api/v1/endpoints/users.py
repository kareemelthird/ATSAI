"""
User management endpoints: CRUD operations for users (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import uuid

from app.db.database import get_db
from app.db.models_users import User, AuditLog
from app.core.auth import (
    hash_password,
    get_current_user
)

router = APIRouter()


# Pydantic Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "viewer"
    department: Optional[str] = None
    job_title: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: str
    status: str
    department: Optional[str]
    job_title: Optional[str]
    is_email_verified: bool
    last_login: Optional[datetime]
    login_count: int
    created_at: Optional[datetime]


class ChangeRoleRequest(BaseModel):
    role: str


# Helper function to check admin access
def require_admin(current_user: User) -> User:
    """Check if user is admin or super admin"""
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Helper function to log audit
async def log_audit_action(db: Session, user: User, action: str, resource_id: str, description: str, old_values=None, new_values=None, request: Request = None):
    """Log audit action"""
    audit = AuditLog(
        id=uuid.uuid4(),
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        action=action,
        resource_type="User",
        resource_id=resource_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent", "") if request else "",
        timestamp=datetime.utcnow(),
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    Optionally filter by role and status
    """
    # Check admin access
    require_admin(current_user)
    
    # Build query
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if status:
        query = query.filter(User.status == status)
    
    # Get users
    users = query.offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            status=user.status,
            department=user.department,
            job_title=user.job_title,
            is_email_verified=user.is_email_verified or False,
            last_login=user.last_login,
            login_count=user.login_count or 0,
            created_at=user.created_at
        )
        for user in users
    ]


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (Admin only)
    """
    # Check admin access
    require_admin(current_user)
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate password
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Create user
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        status="active",
        department=user_data.department,
        job_title=user_data.job_title,
        is_email_verified=False,
        mfa_enabled=False,
        login_count=0,
        failed_login_attempts=0,
        created_at=datetime.utcnow(),
        created_by=current_user.id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log audit
    await log_audit_action(
        db, current_user, "CREATE_USER", str(new_user.id),
        f"Created user {new_user.email} with role {new_user.role}",
        new_values={"email": new_user.email, "role": new_user.role},
        request=request
    )
    
    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        phone=new_user.phone,
        role=new_user.role,
        status=new_user.status,
        department=new_user.department,
        job_title=new_user.job_title,
        is_email_verified=new_user.is_email_verified or False,
        last_login=new_user.last_login,
        login_count=new_user.login_count or 0,
        created_at=new_user.created_at
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only or own profile)
    """
    # Allow users to view their own profile
    if str(current_user.id) != user_id:
        require_admin(current_user)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        status=user.status,
        department=user.department,
        job_title=user.job_title,
        is_email_verified=user.is_email_verified or False,
        last_login=user.last_login,
        login_count=user.login_count or 0,
        created_at=user.created_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user (Admin only or own profile for basic fields)
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    is_own_profile = str(current_user.id) == user_id
    is_admin = current_user.role in ["super_admin", "admin"]
    
    # Only admins can change role and status
    if (user_data.role or user_data.status) and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change role and status"
        )
    
    # Users can only edit their own profile
    if not is_own_profile and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own profile"
        )
    
    # Capture old values
    old_values = {
        "email": user.email,
        "role": user.role,
        "status": user.status
    }
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Log audit
    await log_audit_action(
        db, current_user, "UPDATE_USER", str(user.id),
        f"Updated user {user.email}",
        old_values=old_values,
        new_values=update_data,
        request=request
    )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        status=user.status,
        department=user.department,
        job_title=user.job_title,
        is_email_verified=user.is_email_verified or False,
        last_login=user.last_login,
        login_count=user.login_count or 0,
        created_at=user.created_at
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete/deactivate user (Admin only)
    Actually sets status to INACTIVE rather than deleting
    """
    # Check admin access
    require_admin(current_user)
    
    # Prevent self-deletion
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Deactivate instead of delete (soft delete)
    user.status = "inactive"
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit
    await log_audit_action(
        db, current_user, "DELETE_USER", str(user.id),
        f"Deactivated user {user.email}",
        old_values={"status": "ACTIVE"},
        new_values={"status": "INACTIVE"},
        request=request
    )
    
    return {"message": f"User {user.email} has been deactivated"}


@router.put("/{user_id}/role")
async def change_user_role(
    user_id: str,
    role_data: ChangeRoleRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user role (Admin only)
    Super Admin required to create/modify other Admins
    """
    # Check admin access
    require_admin(current_user)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only Super Admin can create/modify Super Admins and Admins
    # Temporary exception: allow admin@ats.com to self-promote (one-time setup)
    if role_data.role in ["super_admin", "admin"]:
        # Allow admin@ats.com to promote themselves
        if current_user.email == "admin@ats.com" and str(user_id) == str(current_user.id):
            print(f"🔧 Allowing self-promotion for admin@ats.com: {current_user.role} -> {role_data.role}")
        elif current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Super Admin can assign Admin roles"
            )
    
    old_role = user.role
    user.role = role_data.role
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit
    await log_audit_action(
        db, current_user, "CHANGE_ROLE", str(user.id),
        f"Changed role of {user.email} from {old_role} to {role_data.role}",
        old_values={"role": old_role},
        new_values={"role": role_data.role},
        request=request
    )
    
    return {
        "message": f"User role changed from {old_role} to {role_data.role}",
        "user_id": str(user.id),
        "new_role": role_data.role
    }


@router.get("/{user_id}/audit-log")
async def get_user_audit_log(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit log for a specific user (Admin only or own logs)
    """
    # Allow users to view their own logs
    if str(current_user.id) != user_id:
        require_admin(current_user)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Get audit logs
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_uuid
    ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "description": log.description,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "timestamp": log.timestamp,
            "status": log.status
        }
        for log in logs
    ]


@router.put("/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: str,
    new_password: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to reset a user's password
    """
    require_admin(current_user)
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Update password
    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit
    await log_audit_action(
        db, current_user, "RESET_PASSWORD", str(user.id),
        f"Admin reset password for user {user.email}",
        request=request
    )
    
    return {"message": f"Password reset successfully for user {user.email}"}


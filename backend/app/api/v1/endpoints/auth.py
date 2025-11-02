"""
Authentication endpoints: login, register, logout, refresh token, user profile
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
import uuid

from app.db.database import get_db
from app.db.models_users import User, UserSession, AuditLog
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_current_user
)
from app.core.config import settings

router = APIRouter()


# Pydantic Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: str
    status: str
    avatar_url: Optional[str]
    department: Optional[str]
    job_title: Optional[str]
    is_email_verified: bool
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: Optional[datetime]


# Helper function to create session
async def create_user_session(db: Session, user: User, access_token: str, refresh_token: str, request: Request) -> UserSession:
    """Create a new user session"""
    session = UserSession(
        id=uuid.uuid4(),
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token,
        ip_address=getattr(request.client, 'host', None) if hasattr(request, 'client') and request.client else None,
        user_agent=request.headers.get("user-agent", ""),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        is_active=True
    )
    db.add(session)
    db.commit()
    return session


# Helper function to log audit
async def log_audit_action(db: Session, user: User, action: str, description: str, request: Request):
    """Log audit action"""
    audit = AuditLog(
        id=uuid.uuid4(),
        user_id=user.id,
        username=user.username,
        user_role=user.role,  # role is now a string, not enum
        action=action,
        resource_type="User",
        resource_id=str(user.id),
        description=description,
        ip_address=getattr(request.client, 'host', None) if hasattr(request, 'client') and request.client else None,
        user_agent=request.headers.get("user-agent", ""),
        timestamp=datetime.utcnow(),
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Returns access token, refresh token, and user info.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check password
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            user.status = "suspended"  # Use string instead of enum
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to multiple failed login attempts. Try again in 30 minutes."
            )
        
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check account status
    if user.status != "active":  # Use string instead of enum
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}. Please contact administrator."  # Remove .value
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked. Try again in {remaining} minutes."
        )
    
    # Reset failed attempts and unlock
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    user.login_count = (user.login_count or 0) + 1
    user.last_active = datetime.utcnow()
    
    # Unlock if was suspended due to failed attempts
    if user.status == "suspended":  # Use string instead of enum
        user.status = "active"      # Use string instead of enum
    
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create session
    await create_user_session(db, user, access_token, refresh_token, request)
    
    # Log audit
    await log_audit_action(db, user, "LOGIN", f"User {user.email} logged in successfully", request)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "status": user.status
        }
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    By default, creates a VIEWER role account.
    """
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
    
    # Validate password strength (basic validation)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Create new user with VIEWER role by default
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role="viewer",      # Default role as string
        status="active",    # Status as string
        is_email_verified=False,  # Would need email verification flow
        mfa_enabled=False,
        login_count=0,
        failed_login_attempts=0,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens for auto-login after registration
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
    
    # Create session
    await create_user_session(db, new_user, access_token, refresh_token, request)
    
    # Log audit
    await log_audit_action(db, new_user, "REGISTER", f"New user {new_user.email} registered", request)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(new_user.id),
            "email": new_user.email,
            "username": new_user.username,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "role": new_user.role,
            "status": new_user.status
        }
    )


@router.post("/refresh")
async def refresh_token(
    token_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Decode refresh token
        payload = decode_access_token(token_data.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        
        if not user or user.status != "active":  # Use string instead of enum
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Verify refresh token exists in sessions
        session = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.refresh_token == token_data.refresh_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Update session
        session.token = new_access_token
        session.refresh_token = new_refresh_token
        session.expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        session.last_activity = datetime.utcnow()
        
        user.last_active = datetime.utcnow()
        db.commit()
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user and invalidate session
    """
    # Get authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        # Deactivate session
        session = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.token == token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
    
    # Log audit
    await log_audit_action(db, current_user, "LOGOUT", f"User {current_user.email} logged out", request)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile
    """
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        role=current_user.role,
        status=current_user.status,
        avatar_url=current_user.avatar_url,
        department=current_user.department,
        job_title=current_user.job_title,
        is_email_verified=current_user.is_email_verified or False,
        mfa_enabled=current_user.mfa_enabled or False,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit
    await log_audit_action(db, current_user, "CHANGE_PASSWORD", f"User {current_user.email} changed password", request)
    
    return {"message": "Password changed successfully"}

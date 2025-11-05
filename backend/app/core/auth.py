"""
Authentication and Authorization Utilities
JWT token handling, password hashing, role checking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models_users import User, UserSession, AuditLog
from app.core.config import settings

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Alias for backward compatibility
decode_access_token = decode_token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status}"
        )
    
    # Update last activity
    user.last_active = datetime.utcnow()
    db.commit()
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


class RoleChecker:
    """Dependency to check user roles"""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {self.allowed_roles}"
            )
        return current_user


# Role-specific dependencies
require_super_admin = RoleChecker(["super_admin"])
require_admin = RoleChecker(["super_admin", "admin"])
require_hr_manager = RoleChecker(["super_admin", "admin", "hr_manager"])
require_recruiter = RoleChecker(["super_admin", "admin", "hr_manager", "recruiter"])
require_user = RoleChecker(["super_admin", "admin", "hr_manager", "recruiter", "user"])  # Standard logged-in users
require_settings_edit = RoleChecker(["super_admin", "admin"])  # Only admins can edit settings
require_any_user = RoleChecker(["super_admin", "admin", "hr_manager", "recruiter", "user", "viewer"])  # All users


def has_permission(user: User, resource: str, action: str) -> bool:
    """Check if user has permission for a resource action"""
    
    # Super admin has all permissions
    if user.role == "super_admin":
        return True
    
    # Define permissions matrix
    permissions = {
        "admin": {
            "users": ["create", "read", "update", "delete"],
            "candidates": ["create", "read", "update", "delete", "export"],
            "jobs": ["create", "read", "update", "delete"],
            "applications": ["create", "read", "update", "delete"],
            "settings": ["read", "update"],
            "reports": ["read", "export"],
        },
        "hr_manager": {
            "candidates": ["create", "read", "update", "delete", "export"],
            "jobs": ["create", "read", "update", "delete"],
            "applications": ["create", "read", "update", "delete"],
            "reports": ["read", "export"],
        },
        "recruiter": {
            "candidates": ["create", "read", "update"],
            "jobs": ["read"],
            "applications": ["create", "read", "update"],
        },
        "user": {
            "candidates": ["read"],
            "jobs": ["read"],
            "applications": ["read"],
            "files": ["upload"],
            "chat": ["use"],
            "settings": ["read"],  # Can view but not edit
        },
        "viewer": {
            "candidates": ["read"],
            "jobs": ["read"],
            "applications": ["read"],
            "settings": ["read"],  # Can view but not edit
        }
    }
    
    role_permissions = permissions.get(user.role, {})
    resource_permissions = role_permissions.get(resource, [])
    
    return action in resource_permissions


async def log_audit(
    db: Session,
    user: User,
    action: str,
    resource_type: str,
    resource_id: str = None,
    description: str = None,
    old_values: dict = None,
    new_values: dict = None,
    request: Request = None,
    status: str = "success"
):
    """Log an audit trail entry"""
    from app.db.models_users import AuditLog
    
    audit_log = AuditLog(
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        endpoint=str(request.url.path) if request else None,
        http_method=request.method if request else None,
        status=status
    )
    
    db.add(audit_log)
    db.commit()

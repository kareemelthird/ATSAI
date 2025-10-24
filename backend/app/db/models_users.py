"""
User Management Models
Includes User, Role, Permission, and SystemSettings models
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Integer, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"  # Full system access, can manage everything
    ADMIN = "admin"              # Can manage users, settings, view all data
    HR_MANAGER = "hr_manager"    # Can manage candidates, jobs, applications
    RECRUITER = "recruiter"      # Can view and manage assigned candidates/jobs
    VIEWER = "viewer"            # Read-only access to candidates and jobs
    

class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    
    # Role and Status
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    # Profile
    avatar_url = Column(String(500))
    department = Column(String(100))  # HR, Engineering, Sales, etc.
    job_title = Column(String(100))
    
    # Security
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    
    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    
    # Session Management
    last_login = Column(DateTime)
    last_active = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)  # Account lockout
    
    # API Access
    api_key = Column(String(255), unique=True)  # For API authentication
    api_key_expires = Column(DateTime)
    
    # Personal AI Configuration
    personal_groq_api_key = Column(String(255))  # User's personal Groq API key
    use_personal_ai_key = Column(Boolean, default=False)  # Whether to use personal key instead of system default
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Preferences
    preferences = Column(JSON)  # User-specific settings (theme, language, notifications)
    
    # Relationships
    created_by_user = relationship("User", remote_side=[id], backref="created_users")
    audit_logs = relationship("AuditLog", back_populates="user")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    usage_limits = relationship("UserUsageLimit", back_populates="user", uselist=False, cascade="all, delete-orphan")
    usage_history = relationship("UserUsageHistory", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """Track active user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Session Info
    token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True)
    
    # Device/Location Info
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    os = Column(String(100))
    location = Column(String(255))  # City, Country
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    """Audit log for tracking all system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    username = Column(String(100))  # Cached for deleted users
    user_role = Column(String(50))
    
    # What
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    resource_type = Column(String(100))  # User, Candidate, Job, Settings, etc.
    resource_id = Column(String(100))
    
    # Details
    description = Column(Text)
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    
    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    endpoint = Column(String(255))
    http_method = Column(String(10))
    
    # Status
    status = Column(String(20))  # success, failed, error
    error_message = Column(Text)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class SystemSettings(Base):
    """System-wide configuration settings"""
    __tablename__ = "system_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Setting Info
    category = Column(String(100), nullable=False, index=True)  # ai, database, email, security, etc.
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text)  # Stored as JSON string
    data_type = Column(String(50))  # string, number, boolean, json, encrypted
    
    # Metadata
    label = Column(String(255))  # User-friendly label
    description = Column(Text)  # Help text
    is_encrypted = Column(Boolean, default=False)  # Sensitive data
    is_public = Column(Boolean, default=False)  # Can non-admins see this?
    
    # Validation
    validation_rules = Column(JSON)  # min, max, pattern, required, etc.
    default_value = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    updated_by_user = relationship("User", foreign_keys=[updated_by])


class Permission(Base):
    """Fine-grained permissions for resources"""
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Permission Details
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    resource = Column(String(100), nullable=False)  # candidates, jobs, users, settings
    action = Column(String(50), nullable=False)  # create, read, update, delete, export
    
    # Additional Constraints
    conditions = Column(JSON)  # Additional conditions (e.g., can only edit own records)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        {'extend_existing': True}
    )


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # info, warning, success, error
    
    # Action
    action_url = Column(String(500))  # Link to relevant page
    action_text = Column(String(100))  # "View Candidate", "Review Application"
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")

"""
Database models for system settings and user usage tracking
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
from app.db.database import Base


class SystemAISetting(Base):
    """System-wide AI settings controlled by admin from UI"""
    __tablename__ = "system_ai_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text)
    setting_type = Column(String(50), nullable=False)  # 'string', 'number', 'boolean', 'json'
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class UserUsageLimit(Base):
    """Per-user usage limits and current usage"""
    __tablename__ = "user_usage_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    daily_ai_messages_limit = Column(Integer, default=50)
    daily_file_uploads_limit = Column(Integer, default=10)
    messages_used_today = Column(Integer, default=0)
    files_uploaded_today = Column(Integer, default=0)
    last_reset_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="usage_limits")


class UserUsageHistory(Base):
    """Track all user AI usage for analytics and billing"""
    __tablename__ = "user_usage_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    action_type = Column(String(50), nullable=False)  # 'ai_message', 'file_upload', 'resume_parse'
    used_personal_key = Column(Boolean, default=False)
    tokens_used = Column(Integer)
    cost_usd = Column(DECIMAL(10, 6))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Relationship
    user = relationship("User", back_populates="usage_history")

"""
System Settings and Usage Limits Service
Handles all configuration from database (no .env restart needed)
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.db.models_system_settings import SystemAISetting, UserUsageLimit, UserUsageHistory
from fastapi import HTTPException, status


class SystemSettingsService:
    """Service to manage system settings from database"""
    
    @staticmethod
    def get_setting(db: Session, key: str, default: Any = None) -> Any:
        """Get a system setting value"""
        setting = db.query(SystemAISetting).filter(
            SystemAISetting.setting_key == key,
            SystemAISetting.is_active == True
        ).first()
        
        if not setting:
            return default
        
        # Convert to proper type
        if setting.setting_type == 'boolean':
            return setting.setting_value.lower() == 'true'
        elif setting.setting_type == 'number':
            return int(setting.setting_value) if setting.setting_value else default
        elif setting.setting_type == 'json':
            import json
            return json.loads(setting.setting_value) if setting.setting_value else default
        else:
            return setting.setting_value or default
    
    @staticmethod
    def set_setting(db: Session, key: str, value: Any, user_id: str = None):
        """Update a system setting"""
        setting = db.query(SystemAISetting).filter(
            SystemAISetting.setting_key == key
        ).first()
        
        if setting:
            setting.setting_value = str(value)
            setting.updated_at = datetime.utcnow()
            if user_id:
                setting.updated_by = user_id
        else:
            # Create new setting
            setting_type = 'boolean' if isinstance(value, bool) else \
                          'number' if isinstance(value, (int, float)) else 'string'
            setting = SystemAISetting(
                setting_key=key,
                setting_value=str(value),
                setting_type=setting_type,
                updated_by=user_id
            )
            db.add(setting)
        
        db.commit()
        return setting
    
    @staticmethod
    def get_all_settings(db: Session) -> Dict[str, Any]:
        """Get all system settings as a dictionary"""
        settings = db.query(SystemAISetting).filter(
            SystemAISetting.is_active == True
        ).all()
        
        result = {}
        for setting in settings:
            service = SystemSettingsService()
            result[setting.setting_key] = service.get_setting(db, setting.setting_key)
        
        return result


class UsageLimitsService:
    """Service to manage and enforce user usage limits"""
    
    @staticmethod
    def get_or_create_limits(db: Session, user_id: str) -> UserUsageLimit:
        """Get user limits, create if doesn't exist"""
        limits = db.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user_id
        ).first()
        
        if not limits:
            # Get default limits from system settings
            settings_service = SystemSettingsService()
            default_messages = settings_service.get_setting(db, 'default_user_message_limit', 50)
            default_uploads = settings_service.get_setting(db, 'default_user_upload_limit', 10)
            
            limits = UserUsageLimit(
                user_id=user_id,
                daily_ai_messages_limit=default_messages,
                daily_file_uploads_limit=default_uploads
            )
            db.add(limits)
            db.commit()
            db.refresh(limits)
        
        # Reset if it's a new day
        if limits.last_reset_date < date.today():
            limits.messages_used_today = 0
            limits.files_uploaded_today = 0
            limits.last_reset_date = date.today()
            db.commit()
        
        return limits
    
    @staticmethod
    def check_and_increment_message_limit(
        db: Session, 
        user_id: str, 
        using_personal_key: bool
    ) -> bool:
        """
        Check if user can send a message and increment counter
        Returns True if allowed, raises HTTPException if limit reached
        """
        # If using personal key, no limits
        if using_personal_key:
            return True
        
        # Check system limits
        settings_service = SystemSettingsService()
        system_messages_used = settings_service.get_setting(db, 'system_messages_used_today', 0)
        system_limit = settings_service.get_setting(db, 'system_daily_message_limit', 100)
        
        # Reset system counter if new day
        last_reset = settings_service.get_setting(db, 'last_system_reset_date', str(date.today()))
        if last_reset != str(date.today()):
            settings_service.set_setting(db, 'system_messages_used_today', 0)
            settings_service.set_setting(db, 'last_system_reset_date', str(date.today()))
            system_messages_used = 0
        
        # Check if system limit reached
        if system_messages_used >= system_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"System AI limit reached ({system_limit} messages/day). Please use your personal API key or try tomorrow."
            )
        
        # Check user limits
        limits = UsageLimitsService.get_or_create_limits(db, user_id)
        
        if limits.messages_used_today >= limits.daily_ai_messages_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily limit reached ({limits.daily_ai_messages_limit} messages/day). Add your personal API key in Profile for unlimited usage."
            )
        
        # Increment counters
        limits.messages_used_today += 1
        settings_service.set_setting(db, 'system_messages_used_today', system_messages_used + 1)
        db.commit()
        
        return True
    
    @staticmethod
    def check_and_increment_upload_limit(
        db: Session,
        user_id: str,
        using_personal_key: bool
    ) -> bool:
        """Check if user can upload a file and increment counter"""
        if using_personal_key:
            return True
        
        # Check system limits
        settings_service = SystemSettingsService()
        system_uploads_used = settings_service.get_setting(db, 'system_uploads_used_today', 0)
        system_limit = settings_service.get_setting(db, 'system_daily_upload_limit', 20)
        
        # Reset system counter if new day
        last_reset = settings_service.get_setting(db, 'last_system_reset_date', str(date.today()))
        if last_reset != str(date.today()):
            settings_service.set_setting(db, 'system_uploads_used_today', 0)
            settings_service.set_setting(db, 'last_system_reset_date', str(date.today()))
            system_uploads_used = 0
        
        if system_uploads_used >= system_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"System upload limit reached ({system_limit} files/day). Use personal API key for unlimited uploads."
            )
        
        # Check user limits
        limits = UsageLimitsService.get_or_create_limits(db, user_id)
        
        if limits.files_uploaded_today >= limits.daily_file_uploads_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily upload limit reached ({limits.daily_file_uploads_limit} files/day). Add personal API key for unlimited usage."
            )
        
        # Increment counters
        limits.files_uploaded_today += 1
        settings_service.set_setting(db, 'system_uploads_used_today', system_uploads_used + 1)
        db.commit()
        
        return True
    
    @staticmethod
    def log_usage(
        db: Session,
        user_id: str,
        action_type: str,
        used_personal_key: bool,
        tokens_used: int = None,
        cost_usd: float = None,
        extra_data: dict = None
    ):
        """Log usage to history for analytics"""
        history = UserUsageHistory(
            user_id=user_id,
            action_type=action_type,
            used_personal_key=used_personal_key,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            extra_data=extra_data
        )
        db.add(history)
        db.commit()

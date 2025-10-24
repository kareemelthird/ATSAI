"""
Admin Settings API Endpoints
Full control over system configuration from UI
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models_users import User
from app.db.models_system_settings import SystemAISetting, UserUsageLimit, UserUsageHistory
from app.api.v1.endpoints.auth import get_current_user
from app.services.system_settings_service import SystemSettingsService, UsageLimitsService
from datetime import datetime, date

router = APIRouter()


# Pydantic Models
class SystemSettingUpdate(BaseModel):
    setting_key: str
    setting_value: str
    description: Optional[str] = None


class UserLimitUpdate(BaseModel):
    user_id: str
    daily_ai_messages_limit: int
    daily_file_uploads_limit: int


class SystemStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_messages_today: int
    total_uploads_today: int
    system_messages_used: int
    system_uploads_used: int
    system_message_limit: int
    system_upload_limit: int


class UserUsageResponse(BaseModel):
    user_id: str
    user_email: str
    user_name: str
    messages_used_today: int
    files_uploaded_today: int
    messages_limit: int
    uploads_limit: int
    has_personal_key: bool
    last_active: Optional[datetime]


# Helper function to check admin
def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin or super_admin role"""
    from app.db.models_users import UserRole
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user



@router.get("/admin/settings/all")
async def get_all_system_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all system settings for admin panel"""
    settings_service = SystemSettingsService()
    settings = settings_service.get_all_settings(db)
    
    # Get all settings with metadata
    all_settings = db.query(SystemAISetting).all()
    
    result = []
    for setting in all_settings:
        result.append({
            "id": setting.id,
            "key": setting.setting_key,
            "value": setting.setting_value,
            "type": setting.setting_type,
            "description": setting.description,
            "is_active": setting.is_active,
            "updated_at": setting.updated_at
        })
    
    return {
        "settings": result,
        "parsed_values": settings
    }


@router.put("/admin/settings/{setting_key}")
async def update_system_setting(
    setting_key: str,
    update: SystemSettingUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a system setting"""
    settings_service = SystemSettingsService()
    
    try:
        setting = settings_service.set_setting(
            db, 
            setting_key, 
            update.setting_value,
            str(admin.id)
        )
        
        # Update description if provided
        if update.description:
            setting.description = update.description
            db.commit()
        
        return {
            "message": "Setting updated successfully",
            "setting": {
                "key": setting.setting_key,
                "value": setting.setting_value,
                "updated_at": setting.updated_at
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update setting: {str(e)}"
        )


@router.post("/admin/settings/bulk-update")
async def bulk_update_settings(
    settings: List[SystemSettingUpdate],
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update multiple settings at once"""
    settings_service = SystemSettingsService()
    updated = []
    
    for setting_update in settings:
        try:
            setting = settings_service.set_setting(
                db,
                setting_update.setting_key,
                setting_update.setting_value,
                str(admin.id)
            )
            updated.append(setting.setting_key)
        except Exception as e:
            print(f"Error updating {setting_update.setting_key}: {e}")
    
    return {
        "message": f"Updated {len(updated)} settings",
        "updated_keys": updated
    }


@router.get("/admin/stats/system")
async def get_system_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get system-wide statistics"""
    from app.db.models_users import User
    from sqlalchemy import func
    
    settings_service = SystemSettingsService()
    
    # Count users
    total_users = db.query(func.count(User.id)).scalar()
    active_today = db.query(func.count(User.id)).filter(
        func.date(User.last_active) == date.today()
    ).scalar()
    
    # Get system limits and usage
    system_messages_used = settings_service.get_setting(db, 'system_messages_used_today', 0)
    system_uploads_used = settings_service.get_setting(db, 'system_uploads_used_today', 0)
    system_message_limit = settings_service.get_setting(db, 'system_daily_message_limit', 100)
    system_upload_limit = settings_service.get_setting(db, 'system_daily_upload_limit', 20)
    
    # Count today's total usage
    total_messages_today = db.query(func.count(UserUsageHistory.id)).filter(
        func.date(UserUsageHistory.timestamp) == date.today(),
        UserUsageHistory.action_type == 'ai_message'
    ).scalar()
    
    total_uploads_today = db.query(func.count(UserUsageHistory.id)).filter(
        func.date(UserUsageHistory.timestamp) == date.today(),
        UserUsageHistory.action_type == 'file_upload'
    ).scalar()
    
    return {
        "total_users": total_users,
        "active_users_today": active_today or 0,
        "total_messages_today": total_messages_today or 0,
        "total_uploads_today": total_uploads_today or 0,
        "system_messages_used": system_messages_used,
        "system_uploads_used": system_uploads_used,
        "system_message_limit": system_message_limit,
        "system_upload_limit": system_upload_limit,
        "system_message_percentage": round((system_messages_used / system_message_limit * 100) if system_message_limit > 0 else 0, 1),
        "system_upload_percentage": round((system_uploads_used / system_upload_limit * 100) if system_upload_limit > 0 else 0, 1)
    }


@router.get("/admin/users/usage")
async def get_all_users_usage(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get usage stats for all users"""
    from app.db.models_users import User
    from app.services.system_settings_service import SystemSettingsService
    
    users = db.query(User).all()
    usage_data = []
    settings_service = SystemSettingsService()
    
    # Get system default limits
    default_messages = settings_service.get_setting(db, 'default_user_message_limit', 50)
    default_uploads = settings_service.get_setting(db, 'default_user_upload_limit', 10)
    
    for user in users:
        limits = db.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user.id
        ).first()
        
        if limits:
            # Reset daily counters if needed
            if limits.last_reset_date < date.today():
                limits.messages_used_today = 0
                limits.files_uploaded_today = 0
                limits.last_reset_date = date.today()
            
            # Update limits if they're still using old hardcoded defaults (50/10)
            # This ensures existing users get the new system defaults
            if limits.daily_ai_messages_limit == 50 and default_messages != 50:
                limits.daily_ai_messages_limit = default_messages
            if limits.daily_file_uploads_limit == 10 and default_uploads != 10:
                limits.daily_file_uploads_limit = default_uploads
            
            db.commit()
        else:
            # Create default limits using system settings
            limits = UserUsageLimit(
                user_id=user.id,
                daily_ai_messages_limit=default_messages,
                daily_file_uploads_limit=default_uploads
            )
            db.add(limits)
            db.commit()
        
        usage_data.append({
            "user_id": str(user.id),
            "user_email": user.email,
            "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
            "messages_used_today": limits.messages_used_today,
            "files_uploaded_today": limits.files_uploaded_today,
            "messages_limit": limits.daily_ai_messages_limit,
            "uploads_limit": limits.daily_file_uploads_limit,
            "has_personal_key": user.use_personal_ai_key and bool(user.personal_groq_api_key),
            "last_active": user.last_active,
            "role": user.role,
            "status": user.status
        })
    
    return {"users": usage_data}


@router.post("/admin/users/sync-limits")
async def sync_all_user_limits(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Sync all users to current system default limits.
    This updates all users who are still using old default values (50/10)
    to the new system defaults.
    """
    from app.db.models_users import User
    from app.services.system_settings_service import SystemSettingsService
    
    settings_service = SystemSettingsService()
    default_messages = settings_service.get_setting(db, 'default_user_message_limit', 50)
    default_uploads = settings_service.get_setting(db, 'default_user_upload_limit', 10)
    
    updated_count = 0
    users = db.query(User).all()
    
    for user in users:
        limits = db.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user.id
        ).first()
        
        if limits:
            # Update if using old defaults
            if limits.daily_ai_messages_limit == 50 and default_messages != 50:
                limits.daily_ai_messages_limit = default_messages
                updated_count += 1
            if limits.daily_file_uploads_limit == 10 and default_uploads != 10:
                limits.daily_file_uploads_limit = default_uploads
                updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Synced {updated_count} limit values to system defaults",
        "default_messages": default_messages,
        "default_uploads": default_uploads
    }


@router.put("/admin/users/{user_id}/limits")
async def update_user_limits(
    user_id: str,
    update: UserLimitUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update limits for a specific user"""
    limits = db.query(UserUsageLimit).filter(
        UserUsageLimit.user_id == user_id
    ).first()
    
    if not limits:
        limits = UserUsageLimit(user_id=user_id)
        db.add(limits)
    
    limits.daily_ai_messages_limit = update.daily_ai_messages_limit
    limits.daily_file_uploads_limit = update.daily_file_uploads_limit
    db.commit()
    
    return {
        "message": "User limits updated successfully",
        "limits": {
            "messages_limit": limits.daily_ai_messages_limit,
            "uploads_limit": limits.daily_file_uploads_limit
        }
    }


@router.post("/admin/system/reset-daily-limits")
async def reset_daily_limits(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Manually reset all daily limits (usually done automatically at midnight)"""
    settings_service = SystemSettingsService()
    
    # Reset system counters
    settings_service.set_setting(db, 'system_messages_used_today', 0, str(admin.id))
    settings_service.set_setting(db, 'system_uploads_used_today', 0, str(admin.id))
    settings_service.set_setting(db, 'last_system_reset_date', str(date.today()), str(admin.id))
    
    # Reset all user limits
    db.query(UserUsageLimit).update({
        'messages_used_today': 0,
        'files_uploaded_today': 0,
        'last_reset_date': date.today()
    })
    db.commit()
    
    return {
        "message": "All daily limits reset successfully",
        "reset_date": str(date.today())
    }


@router.get("/admin/usage/history")
async def get_usage_history(
    limit: int = 100,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get usage history with optional filtering"""
    query = db.query(UserUsageHistory).order_by(
        UserUsageHistory.timestamp.desc()
    )
    
    if user_id:
        query = query.filter(UserUsageHistory.user_id == user_id)
    
    history = query.limit(limit).all()
    
    result = []
    for record in history:
        user = db.query(User).filter(User.id == record.user_id).first()
        result.append({
            "id": record.id,
            "user_email": user.email if user else "Unknown",
            "action_type": record.action_type,
            "used_personal_key": record.used_personal_key,
            "tokens_used": record.tokens_used,
            "cost_usd": float(record.cost_usd) if record.cost_usd else None,
            "timestamp": record.timestamp,
            "extra_data": record.extra_data
        })
    
    return {"history": result, "total": len(result)}


@router.delete("/admin/settings/{setting_key}")
async def delete_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a system setting"""
    setting = db.query(SystemAISetting).filter(
        SystemAISetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    db.delete(setting)
    db.commit()
    
    return {"message": f"Setting '{setting_key}' deleted successfully"}

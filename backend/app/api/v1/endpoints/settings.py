"""
System Settings Management Endpoints
Allows admins to view and update system configuration stored in .env
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models_users import User, AuditLog, SystemSettings
from app.core.config import settings
import os
from pathlib import Path
from datetime import datetime
import httpx

router = APIRouter()

# Pydantic models
class SettingValue(BaseModel):
    """Model for updating a single setting"""
    value: str = Field(..., description="New value for the setting")

class SettingResponse(BaseModel):
    """Response model for a setting"""
    category: str
    key: str
    value: str
    label: str
    description: str
    data_type: str
    is_encrypted: bool = False
    is_public: bool = False
    requires_restart: bool = False
    provider: Optional[str] = None  # For AI provider-specific settings

class TestAIConnectionRequest(BaseModel):
    """Request to test AI connection"""
    provider: str = Field(..., description="AI provider (groq, deepseek, openrouter)")
    api_key: Optional[str] = Field(None, description="API key to test (optional if use_stored_credentials=True)")
    model: str = Field(..., description="Model to test")
    use_stored_credentials: bool = Field(False, description="Use credentials from .env file instead of provided api_key")

class TestAIConnectionResponse(BaseModel):
    """Response from AI connection test"""
    success: bool
    message: str
    response_time: Optional[float] = None
    model_info: Optional[Dict[str, Any]] = None


# Helper function to check admin access
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify current user is admin"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_env_file_path() -> Path:
    """Get path to .env file"""
    backend_dir = Path(__file__).parent.parent.parent.parent
    env_file = backend_dir / ".env"
    if not env_file.exists():
        # Create from .env.example if it doesn't exist
        example_file = backend_dir / ".env.example"
        if example_file.exists():
            env_file.write_text(example_file.read_text())
    return env_file


def read_env_file() -> Dict[str, str]:
    """Read .env file and return as dictionary"""
    env_file = get_env_file_path()
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


def write_env_file(env_vars: Dict[str, str]):
    """Write dictionary to .env file"""
    env_file = get_env_file_path()
    
    # Read existing file to preserve comments and structure
    lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Update values
    updated_keys = set()
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key = stripped.split('=', 1)[0].strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}\n")
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add new keys that weren't in the file
    for key, value in env_vars.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def get_all_settings_definitions() -> List[Dict[str, Any]]:
    """Get all system settings with their metadata"""
    return [
        # Database Settings
        {
            "category": "database",
            "key": "DATABASE_URL",
            "label": "Database Connection URL",
            "description": "PostgreSQL connection string",
            "data_type": "string",
            "is_encrypted": True,
            "requires_restart": True
        },
        
        # AI Provider Settings
        {
            "category": "ai_provider",
            "key": "AI_PROVIDER",
            "label": "AI Provider",
            "description": "Active AI provider (groq, deepseek, openrouter)",
            "data_type": "select",
            "options": ["groq", "deepseek", "openrouter"],
            "requires_restart": True
        },
        
        # Groq Settings
        {
            "category": "ai_provider",
            "key": "GROQ_API_KEY",
            "label": "Groq API Key",
            "description": "API key for Groq AI service",
            "data_type": "password",
            "is_encrypted": True,
            "requires_restart": True,
            "provider": "groq"
        },
        {
            "category": "ai_provider",
            "key": "GROQ_MODEL",
            "label": "Groq Model",
            "description": "Model to use for Groq (e.g., llama-3.3-70b-versatile, llama-3.1-8b-instant)",
            "data_type": "string",
            "requires_restart": False,
            "provider": "groq"
        },
        
        # DeepSeek Settings
        {
            "category": "ai_provider",
            "key": "DEEPSEEK_API_KEY",
            "label": "DeepSeek API Key",
            "description": "API key for DeepSeek AI service",
            "data_type": "password",
            "is_encrypted": True,
            "requires_restart": True,
            "provider": "deepseek"
        },
        {
            "category": "ai_provider",
            "key": "DEEPSEEK_MODEL",
            "label": "DeepSeek Model",
            "description": "Model to use for DeepSeek (e.g., deepseek-chat)",
            "data_type": "string",
            "requires_restart": False,
            "provider": "deepseek"
        },
        
        # OpenRouter Settings
        {
            "category": "ai_provider",
            "key": "OPENROUTER_API_KEY",
            "label": "OpenRouter API Key",
            "description": "API key for OpenRouter service",
            "data_type": "password",
            "is_encrypted": True,
            "requires_restart": True,
            "provider": "openrouter"
        },
        {
            "category": "ai_provider",
            "key": "OPENROUTER_MODEL",
            "label": "OpenRouter Model",
            "description": "Model to use for OpenRouter (e.g., anthropic/claude-2)",
            "data_type": "string",
            "requires_restart": False,
            "provider": "openrouter"
        },
        
        {
            "category": "ai_provider",
            "key": "USE_MOCK_AI",
            "label": "Use Mock AI",
            "description": "Use mock AI responses for testing (true/false)",
            "data_type": "boolean",
            "requires_restart": True
        },
        
        # AI Instruction Settings
        {
            "category": "ai_provider",
            "key": "ai_resume_analysis_instructions",
            "label": "AI Resume Analysis Instructions",
            "description": "AI instructions for resume analysis and evaluation",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_chat_instructions",
            "label": "AI Chat Instructions",
            "description": "Instructions for general AI chat responses and behavior",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_instructions_arabic",
            "label": "AI Instructions (Arabic)",
            "description": "Base AI instructions for Arabic language responses",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_instructions_english",
            "label": "AI Instructions (English)",
            "description": "Base AI instructions for English language responses",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_hr_context_instructions",
            "label": "AI HR Context Instructions",
            "description": "HR and recruitment context instructions for candidate-related queries",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_evaluation_format_arabic",
            "label": "AI Evaluation Format (Arabic)",
            "description": "Format and guidelines for AI candidate evaluation in Arabic",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_evaluation_format_english",
            "label": "AI Evaluation Format (English)",
            "description": "Format and guidelines for AI candidate evaluation in English",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_fallback_response_arabic",
            "label": "AI Fallback Response (Arabic)",
            "description": "Default response when AI service is unavailable (Arabic)",
            "data_type": "text",
            "requires_restart": False
        },
        {
            "category": "ai_provider",
            "key": "ai_fallback_response_english",
            "label": "AI Fallback Response (English)",
            "description": "Default response when AI service is unavailable (English)",
            "data_type": "text",
            "requires_restart": False
        },
        
        # Usage Limits Settings
        {
            "category": "application",
            "key": "MAX_MESSAGES_PER_USER_DAILY",
            "label": "Max Messages Per User Daily",
            "description": "Maximum number of AI chat messages per user per day",
            "data_type": "number",
            "is_public": True,
            "requires_restart": False
        },
        {
            "category": "application", 
            "key": "MAX_UPLOAD_SIZE_MB",
            "label": "Max Upload Size (MB)",
            "description": "Maximum file upload size in megabytes",
            "data_type": "number",
            "is_public": True,
            "requires_restart": False
        },
        {
            "category": "application",
            "key": "MAX_UPLOADS_PER_USER_DAILY",
            "label": "Max Uploads Per User Daily", 
            "description": "Maximum number of CV uploads per user per day",
            "data_type": "number",
            "is_public": True,
            "requires_restart": False
        },
        {
            "category": "application",
            "key": "ALLOW_USER_CUSTOM_INSTRUCTIONS",
            "label": "Allow User Custom Instructions",
            "description": "Allow users to set custom AI instructions in their profile",
            "data_type": "boolean",
            "is_public": True,
            "requires_restart": False
        },
        
        # Application Settings
        {
            "category": "application",
            "key": "PROJECT_NAME",
            "label": "Project Name",
            "description": "Application name displayed in UI",
            "data_type": "string",
            "requires_restart": False
        },
        
        # Security Settings
        {
            "category": "security",
            "key": "SECRET_KEY",
            "label": "JWT Secret Key",
            "description": "Secret key for JWT token generation (min 32 chars)",
            "data_type": "password",
            "is_encrypted": True,
            "requires_restart": True
        },
        {
            "category": "security",
            "key": "ACCESS_TOKEN_EXPIRE_MINUTES",
            "label": "Access Token Expiry (minutes)",
            "description": "JWT access token expiration time in minutes",
            "data_type": "number",
            "requires_restart": True
        },
        {
            "category": "security",
            "key": "REFRESH_TOKEN_EXPIRE_DAYS",
            "label": "Refresh Token Expiry (days)",
            "description": "JWT refresh token expiration time in days",
            "data_type": "number",
            "requires_restart": True
        },
        
        # CORS Settings
        {
            "category": "security",
            "key": "ALLOWED_ORIGINS",
            "label": "Allowed CORS Origins",
            "description": "Comma-separated list of allowed origins for CORS",
            "data_type": "string",
            "requires_restart": True
        },
        
        # Server Settings
        {
            "category": "server",
            "key": "HOST",
            "label": "Server Host",
            "description": "Server bind address",
            "data_type": "string",
            "requires_restart": True
        },
        {
            "category": "server",
            "key": "PORT",
            "label": "Server Port",
            "description": "Server port number",
            "data_type": "number",
            "requires_restart": True
        },
    ]


@router.get("/", response_model=List[SettingResponse])
async def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all system settings
    Admin only - Now reads from database first, then .env as fallback
    """
    # Get saved settings from database
    db_settings = db.query(SystemSettings).all()
    db_settings_dict = {setting.key: setting.value for setting in db_settings}
    
    # Get environment variables as fallback
    env_vars = read_env_file()
    settings_defs = get_all_settings_definitions()
    
    result = []
    for setting_def in settings_defs:
        key = setting_def["key"]
        # Prefer database value, fallback to env, then empty string
        value = db_settings_dict.get(key) or env_vars.get(key, "")
        
        # Don't mask DATABASE_URL - show actual value for admin
        # Only mask API keys
        if setting_def.get("is_encrypted") and value and "API_KEY" in key:
            value = "***ENCRYPTED***"
        
        result.append(SettingResponse(
            category=setting_def["category"],
            key=key,
            value=value,
            label=setting_def["label"],
            description=setting_def["description"],
            data_type=setting_def["data_type"],
            is_encrypted=setting_def.get("is_encrypted", False),
            is_public=setting_def.get("is_public", False),
            requires_restart=setting_def.get("requires_restart", False),
            provider=setting_def.get("provider")
        ))
    
    return result


@router.get("/public", response_model=List[SettingResponse])
async def get_public_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get public settings that all users can read
    Returns only settings marked as is_public=True
    """
    # Get saved settings from database
    db_settings = db.query(SystemSettings).all()
    db_settings_dict = {setting.key: setting.value for setting in db_settings}
    
    # Get environment variables as fallback
    env_vars = read_env_file()
    settings_defs = get_all_settings_definitions()
    
    result = []
    for setting_def in settings_defs:
        # Only include public settings
        if not setting_def.get("is_public", False):
            continue
            
        key = setting_def["key"]
        # Prefer database value, fallback to env, then empty string
        value = db_settings_dict.get(key) or env_vars.get(key, "")
        
        # Never expose encrypted values to non-admin users
        if setting_def.get("is_encrypted") and value:
            value = "***ENCRYPTED***"
        
        result.append(SettingResponse(
            category=setting_def["category"],
            key=key,
            value=value,
            label=setting_def["label"],
            description=setting_def["description"],
            data_type=setting_def["data_type"],
            is_encrypted=setting_def.get("is_encrypted", False),
            is_public=setting_def.get("is_public", False),
            requires_restart=setting_def.get("requires_restart", False),
            provider=setting_def.get("provider")
        ))
    
    return result


@router.get("/{category}", response_model=List[SettingResponse])
async def get_settings_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get settings by category
    Categories: database, ai_provider, application, security, server
    Admin only
    """
    env_vars = read_env_file()
    settings_defs = get_all_settings_definitions()
    
    result = []
    for setting_def in settings_defs:
        if setting_def["category"] == category:
            key = setting_def["key"]
            value = env_vars.get(key, "")
            
            # Don't mask DATABASE_URL - show actual value for admin
            # Only mask API keys
            if setting_def.get("is_encrypted") and value and "API_KEY" in key:
                value = "***ENCRYPTED***"
            
            result.append(SettingResponse(
                category=setting_def["category"],
                key=key,
                value=value,
                label=setting_def["label"],
                description=setting_def["description"],
                data_type=setting_def["data_type"],
                is_encrypted=setting_def.get("is_encrypted", False),
                is_public=setting_def.get("is_public", False),
                requires_restart=setting_def.get("requires_restart", False),
                provider=setting_def.get("provider")
            ))
    
    return result


@router.put("/{key}")
async def update_setting(
    key: str,
    setting_value: SettingValue,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a single setting
    Admin only - Now stores in database instead of .env file for Vercel compatibility
    """
    # Validate key exists
    settings_defs = get_all_settings_definitions()
    setting_def = next((s for s in settings_defs if s["key"] == key), None)
    
    if not setting_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    # Check if setting exists in database
    existing_setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    
    if existing_setting:
        old_value = existing_setting.value
        existing_setting.value = setting_value.value
        existing_setting.updated_at = datetime.utcnow()
    else:
        # Create new setting record
        old_value = ""
        new_setting = SystemSettings(
            category=setting_def["category"],
            key=key,
            value=setting_value.value,
            data_type=setting_def.get("data_type", "string"),
            label=setting_def.get("label", key),
            description=setting_def.get("description", ""),
            is_encrypted=setting_def.get("is_encrypted", False),
            is_public=setting_def.get("is_public", False),
            default_value=setting_def.get("default_value", "")
        )
        db.add(new_setting)
    
    # Mask old value if encrypted
    old_value_display = "***ENCRYPTED***" if setting_def.get("is_encrypted") and old_value else old_value
    
    # Update environment variable in current process (for immediate use)
    os.environ[key] = setting_value.value
    
    # Log audit trail
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role,
        action="UPDATE",
        resource_type="SYSTEM_SETTING",
        resource_id=key,
        description=f"Updated setting: {setting_def['label']}",
        old_values={"value": old_value_display},
        new_values={"value": "***ENCRYPTED***" if setting_def.get("is_encrypted") else setting_value.value},
        ip_address="127.0.0.1",
        endpoint="/api/v1/settings/" + key,
        http_method="PUT"
    )
    db.add(audit_log)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update setting: {str(e)}"
        )
    
    return {
        "success": True,
        "message": f"Setting '{key}' updated successfully",
        "requires_restart": setting_def.get("requires_restart", False)
    }


@router.post("/test-ai-connection", response_model=TestAIConnectionResponse)
async def test_ai_connection(
    request: TestAIConnectionRequest,
    current_user: User = Depends(require_admin)
):
    """
    Test AI provider connection
    Admin only
    """
    provider_urls = {
        "groq": "https://api.groq.com/openai/v1/chat/completions",
        "deepseek": "https://api.deepseek.com/v1/chat/completions",
        "openrouter": "https://openrouter.ai/api/v1/chat/completions"
    }
    
    api_url = provider_urls.get(request.provider)
    if not api_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {request.provider}"
        )
    
    # Determine which API key to use
    api_key = request.api_key
    
    if request.use_stored_credentials or not api_key:
        # Load API key from .env file
        env_vars = read_env_file()
        api_key_name = f"{request.provider.upper()}_API_KEY"
        api_key = env_vars.get(api_key_name)
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No API key found for {request.provider}. Please configure {api_key_name} in settings."
            )
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": request.model,
        "messages": [
            {"role": "user", "content": "Hello, this is a connection test. Please respond with 'OK'."}
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    try:
        start_time = datetime.now()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        return TestAIConnectionResponse(
            success=True,
            message=f"Successfully connected to {request.provider}",
            response_time=response_time,
            model_info={
                "provider": request.provider,
                "model": request.model,
                "response": result.get("choices", [{}])[0].get("message", {}).get("content", "")
            }
        )
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "error" in error_json:
                error_detail = error_json["error"].get("message", error_detail)
        except:
            pass
        
        return TestAIConnectionResponse(
            success=False,
            message=f"HTTP Error {e.response.status_code}: {error_detail}"
        )
    except Exception as e:
        return TestAIConnectionResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )


@router.get("/categories/list")
async def get_categories(
    current_user: User = Depends(require_admin)
):
    """
    Get list of all setting categories
    Admin only
    """
    settings_defs = get_all_settings_definitions()
    categories = {}
    
    for setting_def in settings_defs:
        category = setting_def["category"]
        if category not in categories:
            categories[category] = {
                "name": category,
                "label": category.replace("_", " ").title(),
                "count": 0
            }
        categories[category]["count"] += 1
    
    return list(categories.values())


@router.get("/public/project-info")
async def get_public_project_info():
    """
    Get public project information (no auth required)
    Returns project name and version for display in UI
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@router.post("/restart-server")
async def restart_server(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Restart the backend server
    This will trigger a graceful restart when running with --reload flag
    Admin only
    
    Note: This only works when the server is running with uvicorn --reload
    In production, you should use a process manager like systemd, supervisor, or pm2
    """
    import sys
    import signal
    
    # Log audit trail
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role,
        action="RESTART",
        resource_type="SYSTEM",
        resource_id="server",
        description=f"Server restart requested by {current_user.username}",
        old_values={},
        new_values={},
        ip_address="127.0.0.1",
        endpoint="/api/v1/settings/restart-server",
        http_method="POST"
    )
    db.add(audit_log)
    db.commit()
    
    # Return success response before restart
    response = {
        "success": True,
        "message": "Server restart initiated. The server will be back online shortly.",
        "timestamp": datetime.now().isoformat()
    }
    
    # Trigger restart by sending SIGTERM to trigger reload
    # This works with uvicorn --reload
    import asyncio
    async def delayed_restart():
        await asyncio.sleep(1)  # Give time for response to be sent
        # Touch the main file to trigger reload
        main_file = Path(__file__).parent.parent.parent / "main.py"
        if main_file.exists():
            main_file.touch()
    
    # Schedule the restart
    asyncio.create_task(delayed_restart())
    
    return response

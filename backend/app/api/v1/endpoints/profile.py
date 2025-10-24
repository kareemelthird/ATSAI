"""
User Profile and Personal Settings Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models_users import User
import httpx
from datetime import datetime

router = APIRouter()


class PersonalAISettings(BaseModel):
    """Model for user's personal AI settings"""
    personal_groq_api_key: Optional[str] = Field(None, description="User's personal Groq API key")
    use_personal_ai_key: bool = Field(False, description="Whether to use personal API key")


class PersonalAISettingsResponse(BaseModel):
    """Response model for AI settings"""
    has_personal_key: bool
    use_personal_ai_key: bool
    key_preview: Optional[str] = None  # Shows only first/last few chars


class TestAIKeyRequest(BaseModel):
    """Request to test an AI API key"""
    api_key: str = Field(..., description="Groq API key to test")


class TestAIKeyResponse(BaseModel):
    """Response from AI key test"""
    success: bool
    message: str
    response_time: Optional[float] = None


@router.get("/ai-settings", response_model=PersonalAISettingsResponse)
async def get_personal_ai_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's personal AI settings
    """
    has_key = bool(current_user.personal_groq_api_key)
    key_preview = None
    
    if has_key and current_user.personal_groq_api_key:
        key = current_user.personal_groq_api_key
        if len(key) > 8:
            key_preview = f"{key[:4]}...{key[-4:]}"
        else:
            key_preview = "***"
    
    return PersonalAISettingsResponse(
        has_personal_key=has_key,
        use_personal_ai_key=current_user.use_personal_ai_key or False,
        key_preview=key_preview
    )


@router.put("/ai-settings")
async def update_personal_ai_settings(
    settings: PersonalAISettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's personal AI settings
    """
    # Update personal API key if provided
    if settings.personal_groq_api_key is not None:
        current_user.personal_groq_api_key = settings.personal_groq_api_key
    
    # Update use_personal_ai_key flag
    current_user.use_personal_ai_key = settings.use_personal_ai_key
    
    db.commit()
    
    return {
        "success": True,
        "message": "Personal AI settings updated successfully"
    }


@router.delete("/ai-settings")
async def delete_personal_ai_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's personal API key
    """
    current_user.personal_groq_api_key = None
    current_user.use_personal_ai_key = False
    
    db.commit()
    
    return {
        "success": True,
        "message": "Personal API key deleted successfully"
    }


@router.post("/ai-settings/test", response_model=TestAIKeyResponse)
async def test_personal_ai_key(
    request: TestAIKeyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test a Groq API key to verify it works
    """
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {request.api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": "Hello! This is a test message. Please respond with 'OK'."}
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
        
        return TestAIKeyResponse(
            success=True,
            message=f"✅ API key is valid! Response time: {response_time:.2f}s",
            response_time=response_time
        )
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "error" in error_json:
                error_detail = error_json["error"].get("message", error_detail)
        except:
            pass
        
        return TestAIKeyResponse(
            success=False,
            message=f"❌ Invalid API key: {error_detail}"
        )
    except Exception as e:
        return TestAIKeyResponse(
            success=False,
            message=f"❌ Connection failed: {str(e)}"
        )


@router.get("/ai-settings/guide")
async def get_groq_setup_guide():
    """
    Get instructions for setting up a free Groq API key
    """
    return {
        "title": "How to Get Your Free Groq API Key",
        "steps": [
            {
                "number": 1,
                "title": "Visit Groq Console",
                "description": "Go to https://console.groq.com/",
                "url": "https://console.groq.com/"
            },
            {
                "number": 2,
                "title": "Sign Up or Log In",
                "description": "Create a free account using your email or Google/GitHub account. No credit card required!"
            },
            {
                "number": 3,
                "title": "Navigate to API Keys",
                "description": "Once logged in, go to the 'API Keys' section in the left sidebar"
            },
            {
                "number": 4,
                "title": "Create New API Key",
                "description": "Click 'Create API Key' button and give it a name (e.g., 'ATS Personal Key')"
            },
            {
                "number": 5,
                "title": "Copy Your Key",
                "description": "Copy the generated API key (starts with 'gsk_'). Store it safely - you won't be able to see it again!"
            },
            {
                "number": 6,
                "title": "Paste in Settings",
                "description": "Come back here and paste your API key in the 'Personal Groq API Key' field"
            }
        ],
        "benefits": [
            "🚀 Fast inference speed (up to 18x faster than OpenAI)",
            "💰 Free tier with generous limits",
            "🔒 Your personal key = your own rate limits",
            "✨ Access to Llama 3.1 models",
            "🎯 No credit card required"
        ],
        "model_info": {
            "name": "llama-3.1-8b-instant",
            "description": "Fast, efficient model perfect for resume parsing and analysis",
            "speed": "~750 tokens/second",
            "context": "128K tokens"
        },
        "support_url": "https://console.groq.com/docs/quickstart"
    }

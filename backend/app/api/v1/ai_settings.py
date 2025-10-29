"""
AI Settings API endpoints for admin to configure AI behavior
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import json

from app.db.database import get_db
from app.db.models_system_settings import SystemAISetting
from app.db.models_users import User
from app.core.auth import get_current_active_user
from pydantic import BaseModel


router = APIRouter()


# Pydantic models
class AISettingCreate(BaseModel):
    setting_key: str
    setting_value: str
    setting_type: str
    description: str


class AISettingUpdate(BaseModel):
    setting_value: str
    is_active: bool = True


class AISettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    setting_type: str
    description: str
    is_active: bool
    updated_at: datetime

    class Config:
        from_attributes = True


def require_admin(current_user: User = Depends(get_current_active_user)):
    """Dependency to require admin role"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage AI settings"
        )
    return current_user


@router.get("/settings", response_model=List[AISettingResponse])
async def get_all_ai_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all AI settings (admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = db.query(SystemAISetting).all()
    return settings


@router.get("/settings/{setting_key}", response_model=AISettingResponse)
async def get_ai_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific AI setting"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    setting = db.query(SystemAISetting).filter(
        SystemAISetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return setting


@router.post("/settings", response_model=AISettingResponse)
async def create_ai_setting(
    setting: AISettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new AI setting (admin only)"""
    # Check if setting already exists
    existing = db.query(SystemAISetting).filter(
        SystemAISetting.setting_key == setting.setting_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Setting with key '{setting.setting_key}' already exists"
        )
    
    new_setting = SystemAISetting(
        setting_key=setting.setting_key,
        setting_value=setting.setting_value,
        setting_type=setting.setting_type,
        description=setting.description,
        is_active=True,
        updated_by=current_user.id
    )
    
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    
    return new_setting


@router.put("/settings/{setting_key}", response_model=AISettingResponse)
async def update_ai_setting(
    setting_key: str,
    setting_update: AISettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update an AI setting (admin only)"""
    setting = db.query(SystemAISetting).filter(
        SystemAISetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.setting_value = setting_update.setting_value
    setting.is_active = setting_update.is_active
    setting.updated_by = current_user.id
    setting.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(setting)
    
    return setting


@router.delete("/settings/{setting_key}")
async def delete_ai_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an AI setting (admin only)"""
    setting = db.query(SystemAISetting).filter(
        SystemAISetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(setting)
    db.commit()
    
    return {"message": f"Setting '{setting_key}' deleted successfully"}


@router.post("/settings/initialize")
async def initialize_default_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Initialize default AI settings if they don't exist"""
    
    default_settings = [
        {
            "setting_key": "resume_analysis_instructions",
            "setting_value": """You are an expert HR assistant and resume analyst. 
Extract comprehensive information from the resume text and return it as detailed JSON.

CRITICAL EXTRACTION RULES:
1. Extract COMPLETE names (first, middle, last) - don't truncate
2. Extract FULL email addresses and phone numbers with country codes if present
3. For work experience: Extract ALL positions, with accurate dates and detailed descriptions
4. For skills: Categorize as technical, soft, or domain-specific
5. For education: Include ALL degrees, certifications, and courses
6. Extract projects with technologies used
7. Extract languages with proficiency levels if mentioned
8. Extract ALL relevant dates in YYYY-MM or YYYY format
9. For work descriptions: Include key responsibilities AND achievements
10. Be thorough and accurate - only extract what's present in the resume
11. Determine career_level based on job titles and experience: Entry (0-2 years), Mid (3-5 years), Senior (6-10 years), Lead (10+ years), Manager/Director/Executive (management roles)
12. Calculate total years_of_experience from all work history (sum of all positions)

REQUIRED FIELDS TO EXTRACT:
- first_name, last_name, email (mandatory)
- phone, location, linkedin, github, portfolio (if available)
- summary (professional summary - 2-3 sentences)
- career_level (Entry/Mid/Senior/Lead/Manager/Director/Executive)
- years_of_experience (total years, integer)
- skills (array with name, category, level)
- work_experience (array with company, title, dates, description, achievements)
- education (array with institution, degree, field, dates)
- projects, certifications, languages (if available)""",
            "setting_type": "string",
            "description": "System instructions for AI resume analysis"
        },
        {
            "setting_key": "chat_system_instructions",
            "setting_value": """You are an intelligent HR assistant with access to a complete ATS database.

YOUR CAPABILITIES:
- Query and analyze candidate profiles, skills, work experience, and education
- Search and filter job postings by title, location, requirements, and status
- Track application statuses and candidate pipelines
- Provide insights on candidate-job matching
- Generate reports and analytics on hiring metrics

AVAILABLE DATA:
- Candidates: Full profiles with contact info, skills, experience, education, projects, certifications
- Jobs: Open positions with requirements, descriptions, locations, and salary ranges
- Applications: All candidate applications with status tracking and interview stages
- Skills: Categorized technical, soft, and domain skills
- Work Experience: Complete employment history with achievements
- Education: Academic background and certifications

RESPONSE GUIDELINES:
1. Always query the database before answering questions about specific data
2. Provide specific examples with names, numbers, and details when available
3. For search queries, show top relevant results with key details
4. When suggesting candidates for jobs, explain the matching logic
5. Be concise but informative - use bullet points for lists
6. If data is not available, clearly state that instead of guessing
7. Suggest follow-up queries when relevant

TONE: Professional, helpful, and data-driven""",
            "setting_type": "string",
            "description": "System instructions for AI chat interactions"
        },
        {
            "setting_key": "ai_temperature",
            "setting_value": "0.3",
            "setting_type": "number",
            "description": "AI temperature (0.0-1.0). Lower = more focused, Higher = more creative"
        },
        {
            "setting_key": "max_tokens",
            "setting_value": "2000",
            "setting_type": "number",
            "description": "Maximum tokens for AI responses"
        },
        {
            "setting_key": "enable_job_matching",
            "setting_value": "true",
            "setting_type": "boolean",
            "description": "Enable AI-powered job matching for candidates"
        },
        {
            "setting_key": "enable_chat_context",
            "setting_value": "true",
            "setting_type": "boolean",
            "description": "Enable conversation history in AI chat"
        }
    ]
    
    created = []
    for setting_data in default_settings:
        existing = db.query(SystemAISetting).filter(
            SystemAISetting.setting_key == setting_data["setting_key"]
        ).first()
        
        if not existing:
            new_setting = SystemAISetting(
                setting_key=setting_data["setting_key"],
                setting_value=setting_data["setting_value"],
                setting_type=setting_data["setting_type"],
                description=setting_data["description"],
                is_active=True,
                updated_by=current_user.id
            )
            db.add(new_setting)
            created.append(setting_data["setting_key"])
    
    db.commit()
    
    return {
        "message": "Default settings initialized",
        "created": created,
        "total": len(created)
    }

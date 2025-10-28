from fastapi import APIRouter
from app.api.v1.endpoints import candidates, resumes, jobs, applications, ai_chat, auth, users, settings, profile, admin_settings
from app.api.v1 import ai_settings

router = APIRouter()

# Authentication & User Management
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(users.router, prefix="/users", tags=["user-management"])
router.include_router(profile.router, prefix="/profile", tags=["user-profile"])
router.include_router(settings.router, prefix="/settings", tags=["system-settings"])
router.include_router(admin_settings.router, tags=["admin-settings"])

# AI Configuration (Admin only)
router.include_router(ai_settings.router, prefix="/ai-settings", tags=["ai-configuration"])

# ATS Features
router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
router.include_router(applications.router, prefix="/applications", tags=["applications"])
router.include_router(ai_chat.router, prefix="/ai", tags=["ai-chat"])

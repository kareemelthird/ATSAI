"""
Import models to ensure they're registered with Base
"""
from app.db.database import Base  # noqa: F401
from app.db.models import (  # noqa: F401
    Candidate,
    Resume,
    Skill,
    WorkExperience,
    Education,
    Project,
    Certification,
    Language,
    AIAnalysis,
    CandidateTag,
    Job,
    Application,
    CandidateJobMatch,
    AIChatQuery,
)
from app.db.models_users import User, UserSession, AuditLog  # noqa: F401
from app.db.models_system_settings import SystemAISetting, UserUsageLimit, UserUsageHistory  # noqa: F401

__all__ = [
    "Base",
    "Candidate",
    "Resume",
    "Skill",
    "CandidateSkill",
    "WorkExperience",
    "Education",
    "Department",
    "Job",
    "JobSkill",
    "Application",
    "Embedding",
    "Keyword",
    "ResumeKeyword",
    "AIQuery",
]

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# Candidate Schemas
class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    current_location: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None  # Changed from HttpUrl to str for flexibility
    github_url: Optional[str] = None     # Changed from HttpUrl to str for flexibility
    portfolio_url: Optional[str] = None  # Changed from HttpUrl to str for flexibility


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    current_location: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    status: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Additional fields from enhanced model
    preferred_locations: Optional[List[str]] = None
    open_to_relocation: Optional[bool] = None
    willing_to_travel: Optional[bool] = None
    professional_summary: Optional[str] = None
    career_level: Optional[str] = None
    availability_status: Optional[str] = None
    notice_period_days: Optional[int] = None
    current_salary_currency: Optional[str] = None
    current_salary_amount: Optional[float] = None
    expected_salary_currency: Optional[str] = None
    expected_salary_amount: Optional[float] = None
    personal_website: Optional[str] = None
    last_active_at: Optional[datetime] = None
    
    # Related data (will be populated by endpoint)
    skills: Optional[List[dict]] = None
    work_experiences: Optional[List[dict]] = None
    educations: Optional[List[dict]] = None
    projects: Optional[List[dict]] = None
    certifications: Optional[List[dict]] = None
    languages: Optional[List[dict]] = None

    class Config:
        from_attributes = True


# Resume Schemas
class ResumeBase(BaseModel):
    original_filename: str
    file_path: str


class ResumeCreate(ResumeBase):
    candidate_id: UUID


class ResumeResponse(ResumeBase):
    id: UUID
    candidate_id: UUID
    extracted_text: Optional[str] = None
    parse_status: str  # Fixed: was parsed_status, should match database column
    upload_date: datetime
    version: int
    ai_analysis_status: Optional[str] = None

    class Config:
        from_attributes = True


# Skill Schemas
class SkillBase(BaseModel):
    name: str
    category: str


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: UUID

    class Config:
        from_attributes = True


# Work Experience Schemas
class WorkExperienceBase(BaseModel):
    company_name: str
    job_title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: Optional[str] = None


class WorkExperienceCreate(WorkExperienceBase):
    candidate_id: UUID


class WorkExperienceResponse(WorkExperienceBase):
    id: UUID
    candidate_id: UUID

    class Config:
        from_attributes = True


# Education Schemas
class EducationBase(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    achievements: Optional[str] = None


class EducationCreate(EducationBase):
    candidate_id: UUID


class EducationResponse(EducationBase):
    id: UUID
    candidate_id: UUID

    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None
    location: Optional[str] = None
    remote_option: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = "USD"
    job_level: Optional[str] = None
    employment_type: str = "Full-time"
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    status: str = "open"
    deadline: Optional[date] = None
    number_of_positions: Optional[int] = 1
    department: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[date] = None
    department: Optional[str] = None


class JobResponse(JobBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Application Schemas
class ApplicationBase(BaseModel):
    candidate_id: UUID
    job_id: UUID
    status: Optional[str] = "submitted"
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    offer_details: Optional[str] = None
    rejection_reason: Optional[str] = None


class ApplicationCreate(BaseModel):
    candidate_id: UUID
    job_id: UUID
    status: Optional[str] = "submitted"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    offer_details: Optional[str] = None
    rejection_reason: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: UUID
    applied_date: datetime
    match_score: Optional[float] = None
    status: str
    match_score: Optional[float] = None
    ai_notes: Optional[str] = None
    hr_notes: Optional[str] = None

    class Config:
        from_attributes = True


# AI Query Schemas
class AIQueryRequest(BaseModel):
    query_text: str
    user_id: Optional[str] = None


class AIQueryResponse(BaseModel):
    id: UUID
    query_text: str
    response: str
    timestamp: datetime
    related_candidates: Optional[List[UUID]] = None  # Changed from str to UUID
    related_jobs: Optional[List[UUID]] = None        # Changed from str to UUID
    execution_time: Optional[float] = None

    class Config:
        from_attributes = True


# Chat/Search Schemas
class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class CandidateInfo(BaseModel):
    """Minimal candidate info for chat responses"""
    id: UUID
    name: str  # Full name
    

class AIChatResponse(BaseModel):
    """Response from AI chat with candidate details"""
    response: str
    candidates: List[CandidateInfo] = []
    jobs: List[UUID] = []


class MatchResult(BaseModel):
    candidate: CandidateResponse
    match_score: float
    matching_skills: List[str]
    reason: str

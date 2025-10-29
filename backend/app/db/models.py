from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Numeric,
    ForeignKey, Boolean, Enum, JSON, ARRAY
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.db.database import Base


# Enums for type safety
class CandidateStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    HIRED = "hired"


class CareerLevel(str, enum.Enum):
    ENTRY = "Entry"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"


class SkillCategory(str, enum.Enum):
    TECHNICAL = "Technical"
    SOFT = "Soft"
    LANGUAGE = "Language"
    CERTIFICATION = "Certification"
    TOOL = "Tool"
    METHODOLOGY = "Methodology"


class ProficiencyLevel(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"
    INTERNSHIP = "Internship"


class ProjectType(str, enum.Enum):
    PERSONAL = "Personal"
    PROFESSIONAL = "Professional"
    OPEN_SOURCE = "Open Source"
    FREELANCE = "Freelance"
    ACADEMIC = "Academic"


class JobStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on-hold"


class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    HIRED = "hired"


# ==================== MAIN MODELS ====================

class Candidate(Base):
    __tablename__ = "candidates"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))  # Increased to handle multiple phone numbers
    
    # Location & Mobility
    current_location = Column(String(255))
    preferred_locations = Column(ARRAY(Text))  # Array of locations
    open_to_relocation = Column(Boolean, default=False)
    willing_to_travel = Column(Boolean, default=False)
    
    # Professional Summary
    professional_summary = Column(Text)
    career_level = Column(String(50))
    years_of_experience = Column(Integer, default=0)
    
    # Availability
    availability_status = Column(String(50))  # "Immediately", "2 weeks", "1 month"
    notice_period_days = Column(Integer)
    
    # Compensation
    current_salary_currency = Column(String(10))
    current_salary_amount = Column(Numeric(12, 2))
    expected_salary_currency = Column(String(10))
    expected_salary_amount = Column(Numeric(12, 2))
    
    # Social & Portfolio
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    personal_website = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime)
    status = Column(String(20), default="active")
    
    # Relationships
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="candidate", cascade="all, delete-orphan")
    languages = relationship("Language", back_populates="candidate", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="candidate", cascade="all, delete-orphan")
    tags = relationship("CandidateTag", back_populates="candidate", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    job_matches = relationship("CandidateJobMatch", back_populates="candidate", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    # Skill Details
    skill_name = Column(String(200), nullable=False)
    skill_category = Column(String(100))  # Technical, Soft, Language, etc.
    skill_type = Column(String(100))  # Programming, Framework, Database, Cloud
    
    # Proficiency
    proficiency_level = Column(String(50))  # Beginner, Intermediate, Advanced, Expert
    years_of_experience = Column(Numeric(4, 1))  # 3.5 years
    last_used_date = Column(Date)
    
    # Context
    acquired_from = Column(String(100))  # Self-taught, Course, Work, Education
    certification_name = Column(String(200))
    certification_date = Column(Date)
    certification_expiry = Column(Date)
    
    # Evidence
    projects_count = Column(Integer, default=0)
    endorsed_by_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="skills")


class WorkExperience(Base):
    __tablename__ = "work_experience"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    # Company Info
    company_name = Column(String(255), nullable=False)
    company_industry = Column(String(100))  # Fintech, Healthcare, E-commerce
    company_size = Column(String(50))  # Startup, SME, Enterprise
    company_location = Column(String(255))
    
    # Role Details
    job_title = Column(String(255), nullable=False)
    job_level = Column(String(50))  # Junior, Mid, Senior, Lead, Manager
    employment_type = Column(String(50))  # Full-time, Part-time, Contract
    
    # Dates
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    duration_months = Column(Integer)
    
    # Responsibilities & Achievements
    responsibilities = Column(Text)
    achievements = Column(ARRAY(Text))  # Array of achievements
    technologies_used = Column(ARRAY(Text))  # Tech stack
    methodologies = Column(ARRAY(Text))  # Agile, Scrum, Waterfall
    
    # Team Context
    team_size = Column(Integer)
    reporting_to = Column(String(100))  # CTO, Engineering Manager
    managed_team_size = Column(Integer)
    
    # Impact Metrics
    key_metrics = Column(JSON)  # {"revenue_increase": "30%", "users": "1M"}
    
    # Reason for leaving
    reason_for_leaving = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="work_experiences")


class Education(Base):
    __tablename__ = "education"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(100), nullable=True)  # Nullable - AI may not extract for short courses/workshops
    field_of_study = Column(String(200), nullable=True)  # Nullable - some courses may not specify field
    specialization = Column(String(200))
    
    start_date = Column(Date)
    end_date = Column(Date)
    graduation_year = Column(Integer)
    
    grade_type = Column(String(50))  # GPA, Percentage, Class
    grade_value = Column(String(20))  # 3.8, 85%, First Class
    
    achievements = Column(ARRAY(Text))  # Dean's List, Scholarships
    relevant_coursework = Column(ARRAY(Text))
    thesis_title = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="educations")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    project_name = Column(String(255), nullable=False)
    project_type = Column(String(100))  # Personal, Professional, Open Source
    
    description = Column(Text)
    role = Column(String(100))  # Developer, Lead, Contributor
    
    technologies_used = Column(ARRAY(Text))
    
    start_date = Column(Date)
    end_date = Column(Date)
    
    project_url = Column(String(500))
    github_url = Column(String(500))
    demo_url = Column(String(500))
    
    highlights = Column(ARRAY(Text))  # Key features or achievements
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    certification_name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=True)  # Made nullable - AI may not extract this
    
    issue_date = Column(Date)
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)
    
    credential_id = Column(String(200))
    credential_url = Column(String(500))
    
    skill_validated = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="certifications")


class Language(Base):
    __tablename__ = "languages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    language_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50))  # Native, Fluent, Professional, Limited
    
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=True)
    can_speak = Column(Boolean, default=True)
    
    certification = Column(String(200))  # TOEFL, IELTS
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="languages")


class AIAnalysis(Base):
    """Stores AI-generated insights about candidates"""
    __tablename__ = "ai_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    analysis_date = Column(DateTime, default=datetime.utcnow)
    ai_model_used = Column(String(100))  # "Groq Llama 3.3 70B"
    
    # AI-Generated Insights
    career_trajectory = Column(Text)  # AI describes career progression
    strengths = Column(ARRAY(Text))  # Top strengths
    areas_of_expertise = Column(ARRAY(Text))  # Key domains
    
    # Scoring (0-100)
    overall_experience_score = Column(Integer)
    technical_depth_score = Column(Integer)
    leadership_score = Column(Integer)
    communication_score = Column(Integer)
    
    # Keywords for matching
    extracted_keywords = Column(ARRAY(Text))
    industry_experience = Column(ARRAY(Text))
    
    # AI Summary
    one_line_summary = Column(Text)  # "Senior Full-Stack Dev with 8 years in Fintech"
    elevator_pitch = Column(Text)  # Longer pitch
    
    # Confidence
    extraction_confidence = Column(Numeric(3, 2))  # 0.95 = 95%
    
    # Raw data for debugging
    raw_analysis = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="ai_analyses")


class CandidateTag(Base):
    """AI-generated smart tags for categorization"""
    __tablename__ = "candidate_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    tag_name = Column(String(100), nullable=False)  # "Cloud Expert", "Team Lead"
    tag_category = Column(String(50))  # expertise, experience_type, soft_skill
    
    confidence = Column(Numeric(3, 2))  # AI confidence
    source = Column(String(50))  # ai_extracted, manual, inferred
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="tags")


class Resume(Base):
    """Stores uploaded resume files"""
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    
    extracted_text = Column(Text)  # Full text extraction
    
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_parsed_date = Column(DateTime)
    
    parse_status = Column(String(20))  # success, failed, pending
    parse_error = Column(Text)
    
    version = Column(Integer, default=1)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")


class Job(Base):
    """Job postings"""
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = Column(String(255), nullable=False)
    company_name = Column(String(255))
    department = Column(String(255))
    
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    
    required_skills = Column(ARRAY(Text))
    preferred_skills = Column(ARRAY(Text))
    
    min_experience_years = Column(Integer)
    max_experience_years = Column(Integer)
    
    location = Column(String(255))
    remote_option = Column(String(50))  # No, Hybrid, Fully Remote
    
    salary_min = Column(Numeric(12, 2))
    salary_max = Column(Numeric(12, 2))
    salary_currency = Column(String(10), default="USD")
    
    job_level = Column(String(50))
    employment_type = Column(String(50), default="Full-time")
    experience_level = Column(String(50))
    
    industry = Column(String(100))
    
    status = Column(String(20), default="open")
    deadline = Column(Date)
    number_of_positions = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("CandidateJobMatch", back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    """Candidate applications to jobs"""
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    
    applied_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="submitted")
    
    cover_letter = Column(Text)
    notes = Column(Text)
    
    # Additional fields for tracking application progress
    interview_date = Column(DateTime)
    offer_details = Column(Text)
    rejection_reason = Column(Text)
    match_score = Column(Numeric(5, 2))  # Calculated match score
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class CandidateJobMatch(Base):
    """AI-powered matching scores between candidates and jobs"""
    __tablename__ = "candidate_job_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    
    # Overall Score
    match_score = Column(Numeric(5, 2))  # 0-100
    
    # Component Scores
    skills_match_score = Column(Numeric(5, 2))
    experience_match_score = Column(Numeric(5, 2))
    location_match_score = Column(Numeric(5, 2))
    salary_match_score = Column(Numeric(5, 2))
    culture_fit_score = Column(Numeric(5, 2))
    
    # AI Explanation
    match_reasoning = Column(Text)
    strengths = Column(ARRAY(Text))  # Why good fit
    gaps = Column(ARRAY(Text))  # What's missing
    
    # Recommendations
    ai_recommendation = Column(String(50))  # Strong Fit, Good Fit, etc.
    interview_focus_areas = Column(ARRAY(Text))
    
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="job_matches")
    job = relationship("Job", back_populates="matches")


class AIChatQuery(Base):
    """Stores AI chat history for learning and improvement"""
    __tablename__ = "ai_chat_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(String(100), default="anonymous")
    query_text = Column(Text, nullable=False)
    query_intent = Column(String(100))  # search_candidates, compare, get_insights
    
    response = Column(Text, nullable=False)
    
    related_candidates = Column(ARRAY(UUID(as_uuid=True)))
    related_jobs = Column(ARRAY(UUID(as_uuid=True)))
    
    execution_time_ms = Column(Integer)
    
    # Feedback
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    was_helpful = Column(Boolean)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

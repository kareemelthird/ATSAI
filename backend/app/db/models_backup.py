from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, 
    ForeignKey, Boolean, Enum, JSON, ARRAY
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.db.database import Base


class CandidateStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    HIRED = "hired"


class ParsedStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class JobType(str, enum.Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


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


class SkillCategory(str, enum.Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    location = Column(String(255))
    summary = Column(Text)
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(CandidateStatus), default=CandidateStatus.ACTIVE)
    
    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    extracted_text = Column(Text)
    parsed_status = Column(Enum(ParsedStatus), default=ParsedStatus.PENDING)
    upload_date = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)
    ai_analysis_status = Column(String(50))
    ai_analysis_result = Column(JSON)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    keywords = relationship("ResumeKeyword", back_populates="resume", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="resume")
    embeddings = relationship("Embedding", back_populates="resume", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(Enum(SkillCategory), nullable=False)
    
    # Relationships
    candidate_skills = relationship("CandidateSkill", back_populates="skill")
    job_skills = relationship("JobSkill", back_populates="skill")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(String(50))
    years_experience = Column(Float)
    source = Column(String(50))  # self-reported, AI-extracted
    
    # Relationships
    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_skills")


class WorkExperience(Base):
    __tablename__ = "work_experience"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    achievements = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="work_experiences")


class Education(Base):
    __tablename__ = "education"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255))
    field_of_study = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    gpa = Column(Float)
    achievements = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="educations")


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    jobs = relationship("Job", back_populates="department")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String(255))
    job_type = Column(Enum(JobType), default=JobType.FULL_TIME)
    salary_range_min = Column(Float)
    salary_range_max = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(Date)
    status = Column(Enum(JobStatus), default=JobStatus.OPEN)
    priority = Column(Integer, default=0)
    
    # Relationships
    department = relationship("Department", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="job", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    importance = Column(String(50))  # required, preferred
    
    # Relationships
    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="job_skills")


class Application(Base):
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    match_score = Column(Float)
    ai_notes = Column(Text)
    hr_notes = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")


class Embedding(Base):
    __tablename__ = "embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # resume, job
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    vector_data = Column(ARRAY(Float))  # Store embedding vector
    embedding_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="embeddings")
    job = relationship("Job", back_populates="embeddings")


class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    word = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100))
    
    # Relationships
    resume_keywords = relationship("ResumeKeyword", back_populates="keyword")


class ResumeKeyword(Base):
    __tablename__ = "resume_keywords"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id"), nullable=False)
    frequency = Column(Integer, default=1)
    relevance_score = Column(Float)
    
    # Relationships
    resume = relationship("Resume", back_populates="keywords")
    keyword = relationship("Keyword", back_populates="resume_keywords")


class AIQuery(Base):
    __tablename__ = "ai_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255))  # Future: link to user table
    query_text = Column(Text, nullable=False)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    related_candidates = Column(JSON)  # Store candidate IDs as JSON array
    related_jobs = Column(JSON)  # Store job IDs as JSON array
    execution_time = Column(Float)  # Query execution time in seconds

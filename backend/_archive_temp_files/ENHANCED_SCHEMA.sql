-- =====================================================
-- AI-OPTIMIZED ATS DATABASE SCHEMA
-- Designed for intelligent candidate matching and analysis
-- =====================================================

-- Core candidate information with AI-friendly fields
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    
    -- Location & Mobility
    current_location VARCHAR(255),
    preferred_locations TEXT[], -- Array of locations willing to work
    open_to_relocation BOOLEAN DEFAULT false,
    willing_to_travel BOOLEAN DEFAULT false,
    
    -- Professional Summary (AI-generated)
    professional_summary TEXT, -- AI extracts key career highlights
    career_level VARCHAR(50), -- Entry, Mid, Senior, Lead, Executive
    
    -- Availability
    availability_status VARCHAR(50), -- Immediately, 2 weeks, 1 month, etc.
    notice_period_days INTEGER,
    
    -- Compensation
    current_salary_currency VARCHAR(10),
    current_salary_amount DECIMAL(12, 2),
    expected_salary_currency VARCHAR(10),
    expected_salary_amount DECIMAL(12, 2),
    
    -- Social & Portfolio
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    personal_website VARCHAR(500),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' -- active, archived, hired
);

-- Skills with detailed proficiency tracking
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    -- Skill Details
    skill_name VARCHAR(200) NOT NULL,
    skill_category VARCHAR(100), -- Technical, Soft, Language, Certification, Tool, etc.
    skill_type VARCHAR(100), -- Programming, Framework, Database, Cloud, etc.
    
    -- Proficiency
    proficiency_level VARCHAR(50), -- Beginner, Intermediate, Advanced, Expert
    years_of_experience DECIMAL(4, 1), -- e.g., 3.5 years
    last_used_date DATE,
    
    -- Context
    acquired_from VARCHAR(100), -- Self-taught, Course, Work, Education
    certification_name VARCHAR(200),
    certification_date DATE,
    certification_expiry DATE,
    
    -- Evidence
    projects_count INTEGER DEFAULT 0,
    endorsed_by_count INTEGER DEFAULT 0, -- LinkedIn endorsements
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Work Experience with rich details
CREATE TABLE work_experience (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    -- Company Info
    company_name VARCHAR(255) NOT NULL,
    company_industry VARCHAR(100), -- Fintech, Healthcare, E-commerce, etc.
    company_size VARCHAR(50), -- Startup, SME, Enterprise
    company_location VARCHAR(255),
    
    -- Role Details
    job_title VARCHAR(255) NOT NULL,
    job_level VARCHAR(50), -- Junior, Mid, Senior, Lead, Manager, Director, etc.
    employment_type VARCHAR(50), -- Full-time, Part-time, Contract, Freelance
    
    -- Dates
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    duration_months INTEGER, -- AI calculates this
    
    -- Responsibilities & Achievements
    responsibilities TEXT, -- What they did
    achievements TEXT[], -- Array of specific achievements
    technologies_used TEXT[], -- Tech stack used
    methodologies TEXT[], -- Agile, Scrum, Waterfall, etc.
    
    -- Team Context
    team_size INTEGER,
    reporting_to VARCHAR(100), -- CTO, Engineering Manager, etc.
    managed_team_size INTEGER, -- If they managed people
    
    -- Impact Metrics (AI extracts numbers)
    key_metrics JSONB, -- {"revenue_increase": "30%", "users_impacted": "1M"}
    
    -- Reason for leaving
    reason_for_leaving VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Education with detailed tracking
CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    institution VARCHAR(255) NOT NULL,
    degree VARCHAR(100) NOT NULL, -- Bachelor, Master, PhD, Diploma, etc.
    field_of_study VARCHAR(200) NOT NULL,
    specialization VARCHAR(200),
    
    start_date DATE,
    end_date DATE,
    graduation_year INTEGER,
    
    grade_type VARCHAR(50), -- GPA, Percentage, Class, etc.
    grade_value VARCHAR(20), -- 3.8, 85%, First Class, etc.
    
    achievements TEXT[], -- Dean's List, Scholarships, etc.
    relevant_coursework TEXT[],
    thesis_title TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects & Portfolio
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    project_name VARCHAR(255) NOT NULL,
    project_type VARCHAR(100), -- Personal, Professional, Open Source, Freelance
    
    description TEXT,
    role VARCHAR(100), -- Developer, Lead, Contributor, etc.
    
    technologies_used TEXT[],
    
    start_date DATE,
    end_date DATE,
    
    project_url VARCHAR(500),
    github_url VARCHAR(500),
    demo_url VARCHAR(500),
    
    highlights TEXT[], -- Key features or achievements
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Certifications
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    certification_name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255) NOT NULL,
    
    issue_date DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT true,
    
    credential_id VARCHAR(200),
    credential_url VARCHAR(500),
    
    skill_validated VARCHAR(200), -- What skill this cert validates
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Languages
CREATE TABLE languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    language_name VARCHAR(100) NOT NULL,
    proficiency_level VARCHAR(50), -- Native, Fluent, Professional, Limited
    
    can_read BOOLEAN DEFAULT true,
    can_write BOOLEAN DEFAULT true,
    can_speak BOOLEAN DEFAULT true,
    
    certification VARCHAR(200), -- TOEFL, IELTS, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Analysis Results (What AI extracted from CV)
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_model_used VARCHAR(100), -- Groq Llama 3.3, etc.
    
    -- AI-Generated Insights
    career_trajectory TEXT, -- AI describes career progression
    strengths TEXT[], -- Top strengths identified
    areas_of_expertise TEXT[], -- Key domains
    
    -- Scoring
    overall_experience_score INTEGER, -- 1-100
    technical_depth_score INTEGER,
    leadership_score INTEGER,
    communication_score INTEGER,
    
    -- Keywords for matching
    extracted_keywords TEXT[],
    industry_experience TEXT[],
    
    -- AI Summary
    one_line_summary TEXT, -- "Senior Full-Stack Developer with 8 years in Fintech"
    elevator_pitch TEXT, -- Longer AI-generated pitch
    
    -- Confidence
    extraction_confidence DECIMAL(3, 2), -- 0.95 = 95% confident
    
    raw_analysis JSONB -- Full AI response for debugging
);

-- Smart Tags (AI-generated categories)
CREATE TABLE candidate_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    tag_name VARCHAR(100) NOT NULL, -- "Cloud Expert", "Team Lead", "Startup Experience"
    tag_category VARCHAR(50), -- expertise, experience_type, soft_skill, industry
    
    confidence DECIMAL(3, 2), -- How confident AI is about this tag
    source VARCHAR(50), -- ai_extracted, manual, inferred
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(candidate_id, tag_name)
);

-- Job Postings (for matching)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    
    description TEXT,
    requirements TEXT,
    
    required_skills TEXT[],
    preferred_skills TEXT[],
    
    min_experience_years INTEGER,
    max_experience_years INTEGER,
    
    location VARCHAR(255),
    remote_option VARCHAR(50), -- No, Hybrid, Fully Remote
    
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    salary_currency VARCHAR(10),
    
    job_level VARCHAR(50),
    employment_type VARCHAR(50),
    
    industry VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'open',
    deadline DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Matching Scores (Candidate to Job)
CREATE TABLE candidate_job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Overall Score
    match_score DECIMAL(5, 2), -- 0-100
    
    -- Component Scores
    skills_match_score DECIMAL(5, 2),
    experience_match_score DECIMAL(5, 2),
    location_match_score DECIMAL(5, 2),
    salary_match_score DECIMAL(5, 2),
    culture_fit_score DECIMAL(5, 2),
    
    -- AI Explanation
    match_reasoning TEXT, -- AI explains why good/bad match
    strengths TEXT[], -- What makes them a good fit
    gaps TEXT[], -- What they're missing
    
    -- Recommendations
    ai_recommendation VARCHAR(50), -- Strong Fit, Good Fit, Possible Fit, Not a Fit
    interview_focus_areas TEXT[], -- What to ask in interview
    
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(candidate_id, job_id)
);

-- Resume Storage
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    original_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    
    extracted_text TEXT, -- Full text extraction
    
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_parsed_date TIMESTAMP,
    
    parse_status VARCHAR(20), -- success, failed, pending
    parse_error TEXT,
    
    version INTEGER DEFAULT 1 -- If candidate uploads multiple versions
);

-- AI Chat History (for learning and improvement)
CREATE TABLE ai_chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id VARCHAR(100) DEFAULT 'anonymous',
    query_text TEXT NOT NULL,
    query_intent VARCHAR(100), -- search_candidates, compare_candidates, get_insights, etc.
    
    response TEXT NOT NULL,
    
    related_candidates UUID[],
    related_jobs UUID[],
    
    execution_time_ms INTEGER,
    
    -- Feedback
    user_rating INTEGER, -- 1-5 stars
    user_feedback TEXT,
    was_helpful BOOLEAN,
    
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_career_level ON candidates(career_level);
CREATE INDEX idx_candidates_location ON candidates USING gin(preferred_locations);
CREATE INDEX idx_skills_name ON skills(skill_name);
CREATE INDEX idx_skills_candidate ON skills(candidate_id);
CREATE INDEX idx_work_exp_candidate ON work_experience(candidate_id);
CREATE INDEX idx_work_exp_company ON work_experience(company_name);
CREATE INDEX idx_work_exp_industry ON work_experience(company_industry);
CREATE INDEX idx_education_candidate ON education(candidate_id);
CREATE INDEX idx_tags_candidate ON candidate_tags(candidate_id);
CREATE INDEX idx_tags_name ON candidate_tags(tag_name);
CREATE INDEX idx_matches_candidate ON candidate_job_matches(candidate_id);
CREATE INDEX idx_matches_job ON candidate_job_matches(job_id);
CREATE INDEX idx_matches_score ON candidate_job_matches(match_score DESC);
CREATE INDEX idx_work_exp_tech ON work_experience USING gin(technologies_used);
CREATE INDEX idx_skills_category ON skills(skill_category);

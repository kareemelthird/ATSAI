-- =============================================================================
-- ATS (Applicant Tracking System) - Clean Database Schema
-- =============================================================================
-- This schema creates a comprehensive ATS database with all enhanced features
-- Use this for fresh installations without hardcoded data or demo credentials
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- USERS AND AUTHENTICATION
-- =============================================================================

-- Users table - Main user management
CREATE TABLE users (
    id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email                       VARCHAR(255) NOT NULL UNIQUE,
    username                    VARCHAR(100) NOT NULL UNIQUE,
    hashed_password             VARCHAR(255) NOT NULL,
    first_name                  VARCHAR(100),
    last_name                   VARCHAR(100),
    phone                       VARCHAR(50),
    role                        VARCHAR(11) NOT NULL CHECK (role IN ('admin', 'hr_manager', 'recruiter')),
    status                      VARCHAR(9) NOT NULL CHECK (status IN ('active', 'inactive', 'suspended')),
    avatar_url                  VARCHAR(500),
    department                  VARCHAR(100),
    job_title                   VARCHAR(100),
    is_email_verified           BOOLEAN DEFAULT FALSE,
    email_verification_token    VARCHAR(255),
    password_reset_token        VARCHAR(255),
    password_reset_expires      TIMESTAMP,
    mfa_enabled                 BOOLEAN DEFAULT FALSE,
    mfa_secret                  VARCHAR(255),
    last_login                  TIMESTAMP,
    last_active                 TIMESTAMP,
    login_count                 INTEGER DEFAULT 0,
    failed_login_attempts       INTEGER DEFAULT 0,
    locked_until                TIMESTAMP,
    api_key                     VARCHAR(255),
    api_key_expires             TIMESTAMP,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID REFERENCES users(id),
    preferences                 JSON,
    personal_groq_api_key       VARCHAR(255),
    use_personal_ai_key         BOOLEAN DEFAULT FALSE
);

-- User sessions for JWT token management
CREATE TABLE user_sessions (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token           VARCHAR(500) NOT NULL UNIQUE,
    refresh_token   VARCHAR(500),
    ip_address      VARCHAR(50),
    user_agent      VARCHAR(500),
    device_type     VARCHAR(50),
    browser         VARCHAR(100),
    os              VARCHAR(100),
    location        VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP NOT NULL,
    last_activity   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE
);

-- User permissions system
CREATE TABLE permissions (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    role        VARCHAR(11) NOT NULL CHECK (role IN ('admin', 'hr_manager', 'recruiter')),
    resource    VARCHAR(100) NOT NULL,
    action      VARCHAR(50) NOT NULL,
    conditions  JSON,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role, resource, action)
);

-- User usage tracking for AI features
CREATE TABLE user_usage_limits (
    id                          SERIAL PRIMARY KEY,
    user_id                     UUID REFERENCES users(id) ON DELETE CASCADE,
    daily_ai_messages_limit     INTEGER DEFAULT 50,
    daily_file_uploads_limit    INTEGER DEFAULT 10,
    messages_used_today         INTEGER DEFAULT 0,
    files_uploaded_today        INTEGER DEFAULT 0,
    last_reset_date             DATE DEFAULT CURRENT_DATE,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User usage history for monitoring
CREATE TABLE user_usage_history (
    id                  SERIAL PRIMARY KEY,
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
    action_type         VARCHAR(50) NOT NULL,
    used_personal_key   BOOLEAN DEFAULT FALSE,
    tokens_used         INTEGER,
    cost_usd            NUMERIC(10, 6),
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data          JSONB
);

-- =============================================================================
-- CANDIDATES AND PROFILES
-- =============================================================================

-- Main candidates table
CREATE TABLE candidates (
    id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    first_name                  VARCHAR(100) NOT NULL,
    last_name                   VARCHAR(100) NOT NULL,
    email                       VARCHAR(255) NOT NULL UNIQUE,
    phone                       VARCHAR(50),
    current_location            VARCHAR(255),
    preferred_locations         TEXT[],
    open_to_relocation          BOOLEAN DEFAULT FALSE,
    willing_to_travel           BOOLEAN DEFAULT FALSE,
    professional_summary        TEXT,
    career_level                VARCHAR(50),
    availability_status         VARCHAR(50),
    notice_period_days          INTEGER,
    current_salary_currency     VARCHAR(10),
    current_salary_amount       NUMERIC(12, 2),
    expected_salary_currency    VARCHAR(10),
    expected_salary_amount      NUMERIC(12, 2),
    linkedin_url                VARCHAR(500),
    github_url                  VARCHAR(500),
    portfolio_url               VARCHAR(500),
    personal_website            VARCHAR(500),
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at              TIMESTAMP,
    status                      VARCHAR(20) DEFAULT 'active',
    years_of_experience         INTEGER DEFAULT 0
);

-- Resume files management
CREATE TABLE resumes (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id        UUID REFERENCES candidates(id) ON DELETE CASCADE,
    original_filename   VARCHAR(500) NOT NULL,
    file_path           VARCHAR(1000) NOT NULL,
    file_size_bytes     BIGINT,
    mime_type           VARCHAR(100),
    extracted_text      TEXT,
    upload_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_parsed_date    TIMESTAMP,
    parse_status        VARCHAR(20),
    parse_error         TEXT,
    version             INTEGER DEFAULT 1
);

-- Work experience
CREATE TABLE work_experience (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id            UUID REFERENCES candidates(id) ON DELETE CASCADE,
    company_name            VARCHAR(255) NOT NULL,
    company_industry        VARCHAR(100),
    company_size            VARCHAR(50),
    company_location        VARCHAR(255),
    job_title               VARCHAR(255) NOT NULL,
    job_level               VARCHAR(50),
    employment_type         VARCHAR(50),
    start_date              DATE,
    end_date                DATE,
    is_current              BOOLEAN DEFAULT FALSE,
    duration_months         INTEGER,
    responsibilities        TEXT,
    achievements            TEXT[],
    technologies_used       TEXT[],
    methodologies           TEXT[],
    team_size               INTEGER,
    reporting_to            VARCHAR(100),
    managed_team_size       INTEGER,
    key_metrics             JSONB,
    reason_for_leaving      VARCHAR(200),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Education
CREATE TABLE education (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id            UUID REFERENCES candidates(id) ON DELETE CASCADE,
    institution             VARCHAR(255),
    degree                  VARCHAR(100),
    field_of_study          VARCHAR(200),
    specialization          VARCHAR(200),
    start_date              DATE,
    end_date                DATE,
    graduation_year         INTEGER,
    grade_type              VARCHAR(50),
    grade_value             VARCHAR(20),
    achievements            TEXT[],
    relevant_coursework     TEXT[],
    thesis_title            TEXT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills management
CREATE TABLE skills (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id            UUID REFERENCES candidates(id) ON DELETE CASCADE,
    skill_name              VARCHAR(200) NOT NULL,
    skill_category          VARCHAR(100),
    skill_type              VARCHAR(100),
    proficiency_level       VARCHAR(50),
    years_of_experience     NUMERIC(4, 1),
    last_used_date          DATE,
    acquired_from           VARCHAR(100),
    certification_name      VARCHAR(200),
    certification_date      DATE,
    certification_expiry    DATE,
    projects_count          INTEGER DEFAULT 0,
    endorsed_by_count       INTEGER DEFAULT 0,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Certifications
CREATE TABLE certifications (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id            UUID REFERENCES candidates(id) ON DELETE CASCADE,
    certification_name      VARCHAR(255) NOT NULL,
    issuing_organization    VARCHAR(255),
    issue_date              DATE,
    expiry_date             DATE,
    is_active               BOOLEAN DEFAULT TRUE,
    credential_id           VARCHAR(200),
    credential_url          VARCHAR(500),
    skill_validated         VARCHAR(200),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Languages
CREATE TABLE languages (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id        UUID REFERENCES candidates(id) ON DELETE CASCADE,
    language_name       VARCHAR(100) NOT NULL,
    proficiency_level   VARCHAR(50),
    can_read            BOOLEAN DEFAULT TRUE,
    can_write           BOOLEAN DEFAULT TRUE,
    can_speak           BOOLEAN DEFAULT TRUE,
    certification       VARCHAR(200),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects
CREATE TABLE projects (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id        UUID REFERENCES candidates(id) ON DELETE CASCADE,
    project_name        VARCHAR(255) NOT NULL,
    project_type        VARCHAR(100),
    description         TEXT,
    role                VARCHAR(100),
    technologies_used   TEXT[],
    start_date          DATE,
    end_date            DATE,
    project_url         VARCHAR(500),
    github_url          VARCHAR(500),
    demo_url            VARCHAR(500),
    highlights          TEXT[],
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidate tags for categorization
CREATE TABLE candidate_tags (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id    UUID REFERENCES candidates(id) ON DELETE CASCADE,
    tag_name        VARCHAR(100) NOT NULL,
    tag_category    VARCHAR(50),
    confidence      NUMERIC(3, 2),
    source          VARCHAR(50),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- JOBS AND POSITIONS
-- =============================================================================

-- Jobs table
CREATE TABLE jobs (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title                   VARCHAR(255) NOT NULL,
    company_name            VARCHAR(255),
    description             TEXT,
    requirements            TEXT,
    required_skills         TEXT[],
    preferred_skills        TEXT[],
    min_experience_years    INTEGER,
    max_experience_years    INTEGER,
    location                VARCHAR(255),
    remote_option           VARCHAR(50),
    salary_min              NUMERIC(12, 2),
    salary_max              NUMERIC(12, 2),
    salary_currency         VARCHAR(10) DEFAULT 'USD',
    job_level               VARCHAR(50),
    employment_type         VARCHAR(50) DEFAULT 'Full-time',
    industry                VARCHAR(100),
    status                  VARCHAR(20) DEFAULT 'open',
    deadline                DATE,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    department              VARCHAR(255),
    responsibilities        TEXT,
    benefits                TEXT,
    experience_level        VARCHAR(50),
    number_of_positions     INTEGER DEFAULT 1
);

-- =============================================================================
-- APPLICATIONS AND MATCHING
-- =============================================================================

-- Job applications
CREATE TABLE applications (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id        UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              UUID REFERENCES jobs(id) ON DELETE CASCADE,
    applied_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status              VARCHAR(50) DEFAULT 'submitted',
    cover_letter        TEXT,
    notes               TEXT,
    interview_date      TIMESTAMP,
    offer_details       TEXT,
    rejection_reason    TEXT,
    match_score         NUMERIC(5, 2),
    UNIQUE(candidate_id, job_id)
);

-- AI-powered candidate-job matching
CREATE TABLE candidate_job_matches (
    id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id                UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id                      UUID REFERENCES jobs(id) ON DELETE CASCADE,
    match_score                 NUMERIC(5, 2),
    skills_match_score          NUMERIC(5, 2),
    experience_match_score      NUMERIC(5, 2),
    location_match_score        NUMERIC(5, 2),
    salary_match_score          NUMERIC(5, 2),
    culture_fit_score           NUMERIC(5, 2),
    match_reasoning             TEXT,
    strengths                   TEXT[],
    gaps                        TEXT[],
    ai_recommendation           VARCHAR(50),
    interview_focus_areas       TEXT[],
    calculated_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, job_id)
);

-- =============================================================================
-- AI AND ANALYTICS
-- =============================================================================

-- AI analysis results
CREATE TABLE ai_analysis (
    id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id                UUID REFERENCES candidates(id) ON DELETE CASCADE,
    analysis_date               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_model_used               VARCHAR(100),
    career_trajectory           TEXT,
    strengths                   TEXT[],
    areas_of_expertise          TEXT[],
    overall_experience_score    INTEGER,
    technical_depth_score       INTEGER,
    leadership_score            INTEGER,
    communication_score         INTEGER,
    extracted_keywords          TEXT[],
    industry_experience         TEXT[],
    one_line_summary            TEXT,
    elevator_pitch              TEXT,
    extraction_confidence       NUMERIC(3, 2),
    raw_analysis                JSONB,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI chat queries and responses
CREATE TABLE ai_chat_queries (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             VARCHAR(100) DEFAULT 'anonymous',
    query_text          TEXT NOT NULL,
    query_intent        VARCHAR(100),
    response            TEXT NOT NULL,
    related_candidates  TEXT[],
    related_jobs        TEXT[],
    execution_time_ms   INTEGER,
    user_rating         INTEGER,
    user_feedback       TEXT,
    was_helpful         BOOLEAN,
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- SYSTEM CONFIGURATION
-- =============================================================================

-- System settings
CREATE TABLE system_settings (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category            VARCHAR(100) NOT NULL,
    key                 VARCHAR(100) NOT NULL,
    value               TEXT,
    data_type           VARCHAR(50),
    label               VARCHAR(255),
    description         TEXT,
    is_encrypted        BOOLEAN DEFAULT FALSE,
    is_public           BOOLEAN DEFAULT FALSE,
    validation_rules    JSON,
    default_value       TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by          UUID REFERENCES users(id),
    UNIQUE(category, key)
);

-- AI-specific system settings
CREATE TABLE system_ai_settings (
    id              SERIAL PRIMARY KEY,
    setting_key     VARCHAR(100) NOT NULL UNIQUE,
    setting_value   TEXT,
    setting_type    VARCHAR(50) NOT NULL,
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by      UUID REFERENCES users(id)
);

-- =============================================================================
-- NOTIFICATIONS AND COMMUNICATION
-- =============================================================================

-- User notifications
CREATE TABLE notifications (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    message             TEXT NOT NULL,
    notification_type   VARCHAR(50),
    action_url          VARCHAR(500),
    action_text         VARCHAR(100),
    is_read             BOOLEAN DEFAULT FALSE,
    read_at             TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP
);

-- =============================================================================
-- AUDIT AND LOGGING
-- =============================================================================

-- Audit logs for security and compliance
CREATE TABLE audit_logs (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    username        VARCHAR(100),
    user_role       VARCHAR(50),
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     VARCHAR(100),
    description     TEXT,
    old_values      JSON,
    new_values      JSON,
    ip_address      VARCHAR(50),
    user_agent      VARCHAR(500),
    endpoint        VARCHAR(255),
    http_method     VARCHAR(10),
    status          VARCHAR(20),
    error_message   TEXT,
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Candidate indexes
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_created_at ON candidates(created_at);
CREATE INDEX idx_candidates_years_experience ON candidates(years_of_experience);
CREATE INDEX idx_candidates_location ON candidates(current_location);

-- Resume indexes
CREATE INDEX idx_resumes_candidate_id ON resumes(candidate_id);
CREATE INDEX idx_resumes_parse_status ON resumes(parse_status);
CREATE INDEX idx_resumes_upload_date ON resumes(upload_date);

-- Work experience indexes
CREATE INDEX idx_work_exp_candidate_id ON work_experience(candidate_id);
CREATE INDEX idx_work_exp_company ON work_experience(company_name);
CREATE INDEX idx_work_exp_dates ON work_experience(start_date, end_date);

-- Skills indexes
CREATE INDEX idx_skills_candidate_id ON skills(candidate_id);
CREATE INDEX idx_skills_name ON skills(skill_name);
CREATE INDEX idx_skills_category ON skills(skill_category);

-- Job indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company_name);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);

-- Application indexes
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_applied_date ON applications(applied_date);

-- Matching indexes
CREATE INDEX idx_matches_candidate_id ON candidate_job_matches(candidate_id);
CREATE INDEX idx_matches_job_id ON candidate_job_matches(job_id);
CREATE INDEX idx_matches_score ON candidate_job_matches(match_score);

-- AI analysis indexes
CREATE INDEX idx_ai_analysis_candidate_id ON ai_analysis(candidate_id);
CREATE INDEX idx_ai_analysis_date ON ai_analysis(analysis_date);

-- Chat queries indexes
CREATE INDEX idx_chat_queries_user_id ON ai_chat_queries(user_id);
CREATE INDEX idx_chat_queries_timestamp ON ai_chat_queries(timestamp);

-- Session indexes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);

-- Audit log indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Update timestamps on candidate updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_candidates_updated_at 
    BEFORE UPDATE ON candidates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- DEFAULT PERMISSIONS DATA
-- =============================================================================

-- Insert default permissions for roles
INSERT INTO permissions (role, resource, action) VALUES
-- Admin permissions
('admin', 'users', 'create'),
('admin', 'users', 'read'),
('admin', 'users', 'update'),
('admin', 'users', 'delete'),
('admin', 'candidates', 'create'),
('admin', 'candidates', 'read'),
('admin', 'candidates', 'update'),
('admin', 'candidates', 'delete'),
('admin', 'jobs', 'create'),
('admin', 'jobs', 'read'),
('admin', 'jobs', 'update'),
('admin', 'jobs', 'delete'),
('admin', 'applications', 'create'),
('admin', 'applications', 'read'),
('admin', 'applications', 'update'),
('admin', 'applications', 'delete'),
('admin', 'settings', 'create'),
('admin', 'settings', 'read'),
('admin', 'settings', 'update'),
('admin', 'settings', 'delete'),
('admin', 'ai_features', 'use'),
('admin', 'reports', 'generate'),

-- HR Manager permissions
('hr_manager', 'candidates', 'create'),
('hr_manager', 'candidates', 'read'),
('hr_manager', 'candidates', 'update'),
('hr_manager', 'jobs', 'create'),
('hr_manager', 'jobs', 'read'),
('hr_manager', 'jobs', 'update'),
('hr_manager', 'applications', 'create'),
('hr_manager', 'applications', 'read'),
('hr_manager', 'applications', 'update'),
('hr_manager', 'ai_features', 'use'),
('hr_manager', 'reports', 'generate'),

-- Recruiter permissions
('recruiter', 'candidates', 'create'),
('recruiter', 'candidates', 'read'),
('recruiter', 'candidates', 'update'),
('recruiter', 'jobs', 'read'),
('recruiter', 'applications', 'create'),
('recruiter', 'applications', 'read'),
('recruiter', 'applications', 'update'),
('recruiter', 'ai_features', 'use');

-- =============================================================================
-- DEFAULT SYSTEM SETTINGS
-- =============================================================================

-- Insert default system settings
INSERT INTO system_settings (category, key, value, data_type, label, description, is_public) VALUES
-- Application settings
('app', 'name', 'ATS System', 'string', 'Application Name', 'Name of the ATS application', true),
('app', 'version', '1.0.0', 'string', 'Application Version', 'Current version of the application', true),
('app', 'environment', 'production', 'string', 'Environment', 'Current environment (development/staging/production)', false),

-- AI settings
('ai', 'enabled', 'true', 'boolean', 'AI Features Enabled', 'Whether AI features are enabled globally', false),
('ai', 'default_model', 'groq/llama3-8b-8192', 'string', 'Default AI Model', 'Default AI model for analysis', false),
('ai', 'max_tokens', '4000', 'integer', 'Max Tokens', 'Maximum tokens for AI responses', false),
('ai', 'temperature', '0.7', 'float', 'AI Temperature', 'Temperature setting for AI responses', false),

-- File upload settings
('uploads', 'max_file_size', '10485760', 'integer', 'Max File Size', 'Maximum file size in bytes (10MB)', false),
('uploads', 'allowed_types', 'pdf,doc,docx,txt', 'string', 'Allowed File Types', 'Comma-separated list of allowed file extensions', false),

-- Security settings
('security', 'password_min_length', '8', 'integer', 'Minimum Password Length', 'Minimum required password length', false),
('security', 'session_timeout', '3600', 'integer', 'Session Timeout', 'Session timeout in seconds', false),
('security', 'max_login_attempts', '5', 'integer', 'Max Login Attempts', 'Maximum failed login attempts before lockout', false),

-- Email settings
('email', 'smtp_enabled', 'false', 'boolean', 'SMTP Enabled', 'Whether email sending is enabled', false),
('email', 'from_address', 'noreply@ats.local', 'string', 'From Address', 'Default from email address', false);

-- =============================================================================
-- SCHEMA COMPLETE
-- =============================================================================

-- Schema creation completed successfully
-- This schema provides:
-- - Complete user management with roles and permissions
-- - Comprehensive candidate profiles with all related data
-- - Job management and application tracking
-- - AI-powered matching and analysis
-- - System configuration and settings
-- - Audit logging and notifications
-- - Performance-optimized indexes
-- - Automatic timestamp updates
-- - Default permissions and settings

-- For fresh installations, create an admin user after running this schema:
-- INSERT INTO users (email, username, hashed_password, first_name, last_name, role, status)
-- VALUES ('admin@yourdomain.com', 'admin', '$hashed_password', 'Admin', 'User', 'admin', 'active');
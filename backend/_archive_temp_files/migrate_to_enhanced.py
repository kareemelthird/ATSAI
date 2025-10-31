"""
Database Migration Script: Upgrade to Enhanced AI-Optimized Schema
This script safely migrates existing data to the new enhanced schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Execute database schema upgrade"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔄 Starting database migration to enhanced schema...")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Step 1: Add new columns to existing candidates table
            print("\n📝 Step 1: Adding new columns to candidates table...")
            
            new_columns = [
                ("preferred_locations", "TEXT[]"),
                ("open_to_relocation", "BOOLEAN DEFAULT false"),
                ("willing_to_travel", "BOOLEAN DEFAULT false"),
                ("professional_summary", "TEXT"),
                ("career_level", "VARCHAR(50)"),
                ("availability_status", "VARCHAR(50)"),
                ("notice_period_days", "INTEGER"),
                ("current_salary_currency", "VARCHAR(10)"),
                ("current_salary_amount", "NUMERIC(12, 2)"),
                ("expected_salary_currency", "VARCHAR(10)"),
                ("expected_salary_amount", "NUMERIC(12, 2)"),
                ("linkedin_url", "VARCHAR(500)"),
                ("github_url", "VARCHAR(500)"),
                ("portfolio_url", "VARCHAR(500)"),
                ("personal_website", "VARCHAR(500)"),
                ("last_active_at", "TIMESTAMP"),
            ]
            
            for col_name, col_type in new_columns:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE candidates 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"   ✅ Added: {col_name}")
                except Exception as e:
                    print(f"   ⚠️  {col_name} - {str(e)}")
            
            # Step 2: Enhance skills table
            print("\n📝 Step 2: Enhancing skills table...")
            
            skills_columns = [
                ("skill_category", "VARCHAR(100)"),
                ("skill_type", "VARCHAR(100)"),
                ("proficiency_level", "VARCHAR(50)"),
                ("years_of_experience", "NUMERIC(4, 1)"),
                ("last_used_date", "DATE"),
                ("acquired_from", "VARCHAR(100)"),
                ("certification_name", "VARCHAR(200)"),
                ("certification_date", "DATE"),
                ("certification_expiry", "DATE"),
                ("projects_count", "INTEGER DEFAULT 0"),
                ("endorsed_by_count", "INTEGER DEFAULT 0"),
            ]
            
            for col_name, col_type in skills_columns:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE skills 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"   ✅ Added: {col_name}")
                except Exception as e:
                    print(f"   ⚠️  {col_name} - {str(e)}")
            
            # Step 3: Enhance work_experience table
            print("\n📝 Step 3: Enhancing work_experience table...")
            
            work_exp_columns = [
                ("company_industry", "VARCHAR(100)"),
                ("company_size", "VARCHAR(50)"),
                ("company_location", "VARCHAR(255)"),
                ("job_level", "VARCHAR(50)"),
                ("employment_type", "VARCHAR(50)"),
                ("duration_months", "INTEGER"),
                ("achievements", "TEXT[]"),
                ("technologies_used", "TEXT[]"),
                ("methodologies", "TEXT[]"),
                ("team_size", "INTEGER"),
                ("reporting_to", "VARCHAR(100)"),
                ("managed_team_size", "INTEGER"),
                ("key_metrics", "JSONB"),
                ("reason_for_leaving", "VARCHAR(200)"),
            ]
            
            for col_name, col_type in work_exp_columns:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE work_experience 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"   ✅ Added: {col_name}")
                except Exception as e:
                    print(f"   ⚠️  {col_name} - {str(e)}")
            
            # Step 4: Enhance education table
            print("\n📝 Step 4: Enhancing education table...")
            
            education_columns = [
                ("specialization", "VARCHAR(200)"),
                ("graduation_year", "INTEGER"),
                ("grade_type", "VARCHAR(50)"),
                ("grade_value", "VARCHAR(20)"),
                ("achievements", "TEXT[]"),
                ("relevant_coursework", "TEXT[]"),
                ("thesis_title", "TEXT"),
            ]
            
            for col_name, col_type in education_columns:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE education 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"   ✅ Added: {col_name}")
                except Exception as e:
                    print(f"   ⚠️  {col_name} - {str(e)}")
            
            # Step 5: Create new tables (projects, certifications, languages, etc.)
            print("\n📝 Step 5: Creating new tables...")
            
            # Projects table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS projects (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    project_name VARCHAR(255) NOT NULL,
                    project_type VARCHAR(100),
                    description TEXT,
                    role VARCHAR(100),
                    technologies_used TEXT[],
                    start_date DATE,
                    end_date DATE,
                    project_url VARCHAR(500),
                    github_url VARCHAR(500),
                    demo_url VARCHAR(500),
                    highlights TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✅ Created: projects table")
            
            # Certifications table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS certifications (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    certification_name VARCHAR(255) NOT NULL,
                    issuing_organization VARCHAR(255) NOT NULL,
                    issue_date DATE,
                    expiry_date DATE,
                    is_active BOOLEAN DEFAULT true,
                    credential_id VARCHAR(200),
                    credential_url VARCHAR(500),
                    skill_validated VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✅ Created: certifications table")
            
            # Languages table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS languages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    language_name VARCHAR(100) NOT NULL,
                    proficiency_level VARCHAR(50),
                    can_read BOOLEAN DEFAULT true,
                    can_write BOOLEAN DEFAULT true,
                    can_speak BOOLEAN DEFAULT true,
                    certification VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✅ Created: languages table")
            
            # AI Analysis table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_model_used VARCHAR(100),
                    career_trajectory TEXT,
                    strengths TEXT[],
                    areas_of_expertise TEXT[],
                    overall_experience_score INTEGER,
                    technical_depth_score INTEGER,
                    leadership_score INTEGER,
                    communication_score INTEGER,
                    extracted_keywords TEXT[],
                    industry_experience TEXT[],
                    one_line_summary TEXT,
                    elevator_pitch TEXT,
                    extraction_confidence NUMERIC(3, 2),
                    raw_analysis JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✅ Created: ai_analysis table")
            
            # Candidate Tags table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS candidate_tags (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    tag_name VARCHAR(100) NOT NULL,
                    tag_category VARCHAR(50),
                    confidence NUMERIC(3, 2),
                    source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(candidate_id, tag_name)
                )
            """))
            print("   ✅ Created: candidate_tags table")
            
            # Resumes table (enhanced)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS resumes_new (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    original_filename VARCHAR(500) NOT NULL,
                    file_path VARCHAR(1000) NOT NULL,
                    file_size_bytes BIGINT,
                    mime_type VARCHAR(100),
                    extracted_text TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_parsed_date TIMESTAMP,
                    parse_status VARCHAR(20),
                    parse_error TEXT,
                    version INTEGER DEFAULT 1
                )
            """))
            print("   ✅ Created: resumes_new table")
            
            # Candidate Job Matches table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS candidate_job_matches (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
                    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
                    match_score NUMERIC(5, 2),
                    skills_match_score NUMERIC(5, 2),
                    experience_match_score NUMERIC(5, 2),
                    location_match_score NUMERIC(5, 2),
                    salary_match_score NUMERIC(5, 2),
                    culture_fit_score NUMERIC(5, 2),
                    match_reasoning TEXT,
                    strengths TEXT[],
                    gaps TEXT[],
                    ai_recommendation VARCHAR(50),
                    interview_focus_areas TEXT[],
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(candidate_id, job_id)
                )
            """))
            print("   ✅ Created: candidate_job_matches table")
            
            # AI Chat Queries table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ai_chat_queries (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(100) DEFAULT 'anonymous',
                    query_text TEXT NOT NULL,
                    query_intent VARCHAR(100),
                    response TEXT NOT NULL,
                    related_candidates UUID[],
                    related_jobs UUID[],
                    execution_time_ms INTEGER,
                    user_rating INTEGER,
                    user_feedback TEXT,
                    was_helpful BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✅ Created: ai_chat_queries table")
            
            # Step 6: Enhance jobs table
            print("\n📝 Step 6: Enhancing jobs table...")
            
            jobs_columns = [
                ("required_skills", "TEXT[]"),
                ("preferred_skills", "TEXT[]"),
                ("min_experience_years", "INTEGER"),
                ("max_experience_years", "INTEGER"),
                ("remote_option", "VARCHAR(50)"),
                ("salary_min", "NUMERIC(12, 2)"),
                ("salary_max", "NUMERIC(12, 2)"),
                ("salary_currency", "VARCHAR(10)"),
                ("job_level", "VARCHAR(50)"),
                ("industry", "VARCHAR(100)"),
                ("deadline", "DATE"),
            ]
            
            for col_name, col_type in jobs_columns:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE jobs 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"   ✅ Added: {col_name}")
                except Exception as e:
                    print(f"   ⚠️  {col_name} - {str(e)}")
            
            # Step 7: Create indexes for performance
            print("\n📝 Step 7: Creating indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_skills_candidate ON skills(candidate_id)",
                "CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(skill_name)",
                "CREATE INDEX IF NOT EXISTS idx_work_exp_candidate ON work_experience(candidate_id)",
                "CREATE INDEX IF NOT EXISTS idx_work_exp_company ON work_experience(company_name)",
                "CREATE INDEX IF NOT EXISTS idx_education_candidate ON education(candidate_id)",
                "CREATE INDEX IF NOT EXISTS idx_tags_candidate ON candidate_tags(candidate_id)",
                "CREATE INDEX IF NOT EXISTS idx_tags_name ON candidate_tags(tag_name)",
                "CREATE INDEX IF NOT EXISTS idx_matches_score ON candidate_job_matches(match_score DESC)",
            ]
            
            for idx_sql in indexes:
                try:
                    conn.execute(text(idx_sql))
                    print(f"   ✅ Created index")
                except Exception as e:
                    print(f"   ⚠️  Index creation: {str(e)}")
            
            # Commit all changes
            trans.commit()
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print("\n📊 New Tables Added:")
            print("   • projects")
            print("   • certifications")
            print("   • languages")
            print("   • ai_analysis")
            print("   • candidate_tags")
            print("   • candidate_job_matches")
            print("   • ai_chat_queries")
            print("\n📈 Enhanced Tables:")
            print("   • candidates (16 new fields)")
            print("   • skills (11 new fields)")
            print("   • work_experience (14 new fields)")
            print("   • education (7 new fields)")
            print("   • jobs (11 new fields)")
            print("\n🚀 Ready for AI-powered resume analysis!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            print("Database rolled back to previous state.")
            raise

if __name__ == "__main__":
    run_migration()

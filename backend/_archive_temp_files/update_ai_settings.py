"""
Script to update AI settings in the database with enhanced instructions
Run this after updating the codebase to ensure settings are current
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models_system_settings import SystemAISetting
from datetime import datetime

def update_ai_settings():
    """Update AI settings with enhanced instructions"""
    db = SessionLocal()
    
    try:
        # Updated resume analysis instructions
        resume_instructions = """You are an expert HR assistant and resume analyst. 
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
- projects, certifications, languages (if available)"""
        
        # Check if setting exists
        setting = db.query(SystemAISetting).filter(
            SystemAISetting.setting_key == "resume_analysis_instructions"
        ).first()
        
        if setting:
            print("✓ Found existing 'resume_analysis_instructions' setting")
            setting.setting_value = resume_instructions
            setting.updated_at = datetime.utcnow()
            print("✓ Updated with enhanced instructions (includes career_level and years_of_experience)")
        else:
            print("✗ Setting 'resume_analysis_instructions' not found")
            print("Creating new setting...")
            setting = SystemAISetting(
                setting_key="resume_analysis_instructions",
                setting_value=resume_instructions,
                setting_type="string",
                description="System instructions for AI resume analysis (includes career_level and years_of_experience)",
                is_active=True
            )
            db.add(setting)
            print("✓ Created new 'resume_analysis_instructions' setting")
        
        db.commit()
        print("\n✅ AI settings updated successfully!")
        print("\nNEXT STEPS:")
        print("1. Restart the backend server to apply changes")
        print("2. Upload a new resume to test career_level extraction")
        print("3. Check that 'Mid', 'Senior', etc. appear under candidate name")
        
    except Exception as e:
        print(f"\n❌ Error updating settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("UPDATING AI SETTINGS")
    print("=" * 60)
    update_ai_settings()

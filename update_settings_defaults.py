#!/usr/bin/env python3

import requests
import json

def update_settings_with_defaults():
    """Update existing empty settings with proper default values"""
    
    print("🔧 Updating settings with default values...")
    print("-" * 60)
    
    # Login first
    auth_data = {"email": "admin@ats.com", "password": "admin123"}
    
    auth_response = requests.post(
        "https://atsai-jade.vercel.app/api/v1/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.text}")
        return
        
    token = auth_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Default values for the existing settings
    default_values = {
        "AI_PROVIDER": "openrouter",
        "GROQ_MODEL": "llama-3.1-70b-versatile", 
        "DEEPSEEK_MODEL": "deepseek-chat",
        "OPENROUTER_MODEL": "anthropic/claude-3.5-sonnet",
        "USE_MOCK_AI": "false",
        "PROJECT_NAME": "ATS AI",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7", 
        "ALLOWED_ORIGINS": "https://atsai-jade.vercel.app,http://localhost:3000",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "ai_resume_analysis_instructions": """You are an expert HR assistant and resume analyst. 
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
12. Calculate total years_of_experience from all work history (sum of all positions)""",
        "chat_system_instructions": """You are an AI assistant for an Applicant Tracking System (ATS). 
Your role is to help HR professionals, recruiters, and hiring managers with:

1. Resume analysis and candidate evaluation
2. Job requirement matching
3. Interview question suggestions
4. HR best practices and compliance
5. Recruitment strategy advice

Be professional, accurate, and helpful. Always provide evidence-based recommendations when evaluating candidates or suggesting improvements."""
    }
    
    print(f"🔧 Updating {len(default_values)} settings with default values...")
    
    success_count = 0
    for setting_key, default_value in default_values.items():
        print(f"\n   Updating: {setting_key}")
        try:
            update_data = {"setting_value": default_value}
            response = requests.put(
                f"https://atsai-jade.vercel.app/api/v1/settings/{setting_key}",
                json=update_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Updated successfully")
                success_count += 1
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🔧 Updated {success_count}/{len(default_values)} settings successfully!")
    
    if success_count > 0:
        print("🔧 Settings have been populated with default values.")
        print("🔧 You can now refresh the Settings page to see the populated values.")
        print("🔧 Remember to add your API keys in the Settings page!")

if __name__ == "__main__":
    update_settings_with_defaults()
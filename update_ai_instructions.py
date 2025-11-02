#!/usr/bin/env python3
"""
Update the existing AI instruction settings with proper values
"""
import requests

def update_ai_instructions():
    base_url = "https://atsai-jade.vercel.app"
    
    print("📝 Updating AI Instruction Settings")
    print("=" * 40)
    
    # Login
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Update resume analysis instructions
    resume_instructions = '''You are an expert HR assistant that analyzes resumes and extracts structured data.

IMPORTANT: Return ONLY a valid JSON object with the following structure:

{
  "personal_info": {
    "name": "Full Name",
    "email": "email@domain.com",
    "phone": "phone number",
    "location": "city, country",
    "linkedin": "LinkedIn URL",
    "github": "GitHub URL"
  },
  "summary": "Professional summary highlighting key achievements",
  "years_experience": 5,
  "skills": [
    {"name": "Python", "category": "technical"},
    {"name": "Communication", "category": "soft"}
  ],
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name", 
      "duration": "2020-2023",
      "description": "Key responsibilities and achievements"
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science",
      "institution": "University Name",
      "year": "2020"
    }
  ],
  "languages": [
    {"language": "English", "proficiency": "Native"},
    {"language": "Arabic", "proficiency": "Fluent"}
  ]
}

Extract information accurately from the resume text. If information is missing, omit that field.'''

    print("\n📝 Updating resume analysis instructions...")
    update_response = requests.put(
        f"{base_url}/api/v1/settings/ai_resume_analysis_instructions",
        json={"value": resume_instructions},
        headers=headers
    )
    
    if update_response.status_code == 200:
        print("✅ Resume analysis instructions updated")
    else:
        print(f"❌ Failed to update resume instructions: {update_response.text}")
    
    # Update chat system instructions
    chat_instructions = '''You are "ATS Smart Assistant", a friendly and intelligent HR assistant.

Your role is to help recruiters find the best candidates and analyze their profiles.

Guidelines:
- Be conversational and professional
- If asked about specific jobs or candidates, search the database accurately
- Only provide information that exists in the database
- If no suitable candidates are found, suggest clarifying the requirements
- For Arabic queries, respond in Arabic
- For English queries, respond in English
- Keep responses concise but helpful
- Ask clarifying questions when needed

When searching for candidates:
1. Understand the job requirements clearly
2. Search based on skills, experience, and qualifications
3. Present the most relevant candidates first
4. Explain why each candidate is a good match'''

    print("\n💬 Updating chat system instructions...")
    update_response = requests.put(
        f"{base_url}/api/v1/settings/chat_system_instructions",
        json={"value": chat_instructions},
        headers=headers
    )
    
    if update_response.status_code == 200:
        print("✅ Chat system instructions updated")
    else:
        print(f"❌ Failed to update chat instructions: {update_response.text}")
    
    # Verify updates
    print("\n🔍 Verifying updates...")
    settings_response = requests.get(f"{base_url}/api/v1/settings", headers=headers)
    if settings_response.status_code == 200:
        settings = settings_response.json()
        instruction_settings = [s for s in settings if 'instruction' in s.get('key', '').lower()]
        
        for setting in instruction_settings:
            value_length = len(setting.get('value', ''))
            print(f"   ✅ {setting.get('label')}: {value_length} characters")
    
    print("\n🎉 AI Instructions are now configured and ready to use!")

if __name__ == "__main__":
    update_ai_instructions()
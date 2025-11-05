import httpx
from typing import Dict, Any, List
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import models
import json
import re
from datetime import datetime


async def call_ai_api(prompt: str, system_message: str = None, user_api_key: str = None, db: Session = None) -> str:
    """
    Call AI API (OpenRouter or DeepSeek) for completions
    Args:
        user_api_key: Optional user's personal API key
        db: Database session to get system API key from database
    """
    # If USE_MOCK_AI is enabled, skip API and use mock responses
    if settings.USE_MOCK_AI:
        print("🤖 Using mock AI response (USE_MOCK_AI=true)")
        
        # Check if this is a resume analysis request (has structured JSON format request)
        if ("```json" in prompt.lower() or 
            ("resume" in prompt.lower() and "extract" in prompt.lower()) or
            ("analyze the resume data" in prompt.lower()) or
            ("analyze this resume" in prompt.lower()) or
            ("structured information" in prompt.lower())):
            
            # Try to extract basic info from the actual CV text for better mock response
            extracted_name = "John"
            extracted_lastname = "Smith"
            extracted_email = "john.smith@email.com"
            extracted_phone = "+1-555-123-4567"
            
            # Simple extraction from prompt text
            lines = prompt.split('\n')
            name_found = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for name (only if not found yet)
                if not name_found and line and len(line) < 50:  # Likely name line
                    words = line.split()
                    if len(words) >= 2 and len(words) <= 4:
                        # Check if it looks like a name (not email, phone, title)
                        if not any(char in line.lower() for char in ['@', '.com', '+', '(', ')', 'email:', 'phone:', 'developer', 'engineer', 'manager']):
                            if not line.lower().startswith(('analyze', 'extract', 'return')):
                                extracted_name = words[0]
                                extracted_lastname = ' '.join(words[1:]) if len(words) > 1 else ""
                                name_found = True
                
                # Look for email
                if '@' in line and '.com' in line:
                    email_match = line.split()
                    for word in email_match:
                        if '@' in word and '.com' in word:
                            extracted_email = word.strip(':').strip()
                            break
                
                # Look for phone
                if any(char in line for char in ['+', '(', ')', '-']) and any(char.isdigit() for char in line):
                    if 'phone' in line.lower() or '+' in line:
                        phone_parts = line.split()
                        for part in phone_parts:
                            if any(char.isdigit() for char in part) and len(part) > 5:
                                extracted_phone = part.strip(':').strip()
                                break
            
            return f"""```json
{{
  "first_name": "{extracted_name}",
  "last_name": "{extracted_lastname}",
  "email": "{extracted_email}",
  "phone": "{extracted_phone}",
  "location": "Cairo, Egypt",
  "linkedin": "linkedin.com/in/profile",
  "summary": "Experienced developer with expertise in modern technologies and web development.",
  "career_level": "Mid",
  "years_of_experience": 3,
  "skills": [
    {{"name": "SharePoint Online", "category": "technical", "level": "Advanced"}},
    {{"name": "Power Platform", "category": "technical", "level": "Intermediate"}},
    {{"name": "Power Automate", "category": "technical", "level": "Advanced"}},
    {{"name": "JavaScript", "category": "technical", "level": "Intermediate"}},
    {{"name": "C#", "category": "technical", "level": "Intermediate"}},
    {{"name": "Communication", "category": "soft", "level": "Expert"}}
  ],
  "work_experience": [
    {{
      "company": "Tech Solutions Ltd",
      "title": "SharePoint Developer",
      "start_date": "2023-01",
      "end_date": "Present",
      "description": "• Developed SharePoint Online solutions\\n• Built Power Platform applications\\n• Implemented automated workflows",
      "is_current": true,
      "location": "Cairo, Egypt"
    }}
  ],
  "education": [
    {{
      "institution": "Cairo University",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "start_date": "2018",
      "graduation_date": "2022-06",
      "grade": "Very Good"
    }}
  ]
}}
```"""
        else:
            # For chat queries, provide conversational responses
            
            # Extract the original user query from the complex prompt
            original_query = prompt
            if "Current Question:" in prompt:
                # Extract just the user's question from the complex prompt
                lines = prompt.split('\n')
                for line in lines:
                    if line.strip().startswith("Current Question:"):
                        original_query = line.replace("Current Question:", "").strip()
                        break
            
            # Detect language to provide appropriate response
            def detect_language(text: str) -> str:
                arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
                english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
                total_chars = arabic_chars + english_chars
                
                if total_chars == 0:
                    return "english"
                
                arabic_ratio = arabic_chars / total_chars
                return "arabic" if arabic_ratio > 0.3 else "english"
            
            user_language = detect_language(original_query)
            
            # Handle common questions about AI's role
            role_questions_arabic = ["ماهي وظيفتك", "من أنت", "ما دورك", "اخبرني عن نفسك"]
            role_questions_english = ["what is your job", "who are you", "what do you do", "tell me about yourself"]
            
            is_role_question = any(q in original_query.lower() for q in role_questions_arabic + role_questions_english)
            
            if is_role_question:
                if user_language == "arabic":
                    mock_response = get_ai_setting(db, "ai_mock_role_response_arabic", 
                        default_value="مساعد ذكي للموارد البشرية") if db else "مساعد ذكي"
                    return mock_response
                else:
                    mock_response = get_ai_setting(db, "ai_mock_role_response_english", 
                        default_value="AI HR assistant") if db else "AI assistant"
                    return mock_response
            
            # For other chat queries, provide helpful responses
            if "CANDIDATE PROFILES:" in prompt and not prompt.split("CANDIDATE PROFILES:")[1].strip().startswith("IMPORTANT"):
                # Parse candidate names from the actual candidate data section
                import re
                candidate_section = prompt.split("CANDIDATE PROFILES:")[1].split("IMPORTANT:")[0]
                candidates = re.findall(r'Candidate: ([^\n]+)', candidate_section)
                
                # Parse jobs from the context if available
                jobs = []
                if "AVAILABLE JOBS:" in prompt:
                    jobs_section = prompt.split("AVAILABLE JOBS:")[1].split("APPLICATIONS STATUS:")[0] if "APPLICATIONS STATUS:" in prompt else prompt.split("AVAILABLE JOBS:")[1]
                    jobs = re.findall(r'Job: ([^\n]+)', jobs_section)
                elif "الوظائف المتاحة:" in prompt:
                    jobs_section = prompt.split("الوظائف المتاحة:")[1].split("APPLICATIONS STATUS:")[0] if "APPLICATIONS STATUS:" in prompt else prompt.split("الوظائف المتاحة:")[1]
                    jobs = re.findall(r'الوظيفة: ([^\n]+)', jobs_section)
                
                # Only provide mock response if we have actual database content
                if candidates and len(candidates) > 0:
                    if user_language == "arabic":
                        response = f"وجدت {len(candidates)} مرشح في قاعدة البيانات:\n\n"
                        for i, name in enumerate(candidates[:3], 1):
                            response += f"{i}. **{name}**: "
                            if "kareem" in name.lower() and "hassan" in name.lower():
                                response += "مطور خبير بمهارات في Python وFastAPI وReact وJavaScript وPostgreSQL والتواصل. يعمل في TechCorp Solutions كمطور أول.\n\n"
                            else:
                                response += "مطور متكامل بمهارات تقنية قوية وخبرة مهنية.\n\n"
                        
                        if jobs:
                            response += f"\nالوظائف المتاحة ({len(jobs)}):\n"
                            for i, job in enumerate(jobs[:3], 1):
                                response += f"• {job}\n"
                            if len(jobs) > 3:
                                response += f"... و {len(jobs) - 3} وظائف أخرى\n"
                            response += "\nيمكنني تقييم المرشحين لأي من هذه الوظائف والتوصية بأنسب المرشحين لكل منصب."
                        else:
                            response += "\nملاحظة: لا توجد وظائف مفتوحة حالياً في النظام."
                            
                        response += "\n\nهل تريد مني تقييم أي من هؤلاء المرشحين لوظيفة معينة؟"
                    else:
                        response = f"I found {len(candidates)} candidate(s) in the database:\n\n"
                        for i, name in enumerate(candidates[:3], 1):
                            response += f"{i}. **{name}**: "
                            if "kareem" in name.lower() and "hassan" in name.lower():
                                response += "Experienced developer with skills in Python, FastAPI, React, JavaScript, PostgreSQL, and Communication. Works at TechCorp Solutions as a Senior Software Developer.\n\n"
                            else:
                                response += "Full-stack developer with strong technical skills and professional experience.\n\n"
                        
                        if jobs:
                            response += f"\nAvailable Positions ({len(jobs)}):\n"
                            for i, job in enumerate(jobs[:3], 1):
                                response += f"• {job}\n"
                            if len(jobs) > 3:
                                response += f"... and {len(jobs) - 3} more positions\n"
                            response += "\nI can evaluate candidates for any of these positions and recommend the best fit for each role."
                        else:
                            response += "\nNote: No active job openings are currently available in the system."
                            
                        response += "\n\nWould you like me to evaluate any of these candidates for a specific position?"
                    return response
            
            # Default conversational response
            if user_language == "arabic":
                default_response = get_ai_setting(db, "ai_mock_default_response_arabic", 
                    default_value="مساعد توظيف") if db else "مساعد"
                return default_response
            else:
                default_response = get_ai_setting(db, "ai_mock_default_response_english", 
                    default_value="HR assistant") if db else "Assistant"
                return default_response
    
    # Check if personal API key is required
    require_personal_key = False
    if db:
        require_setting = get_ai_setting(db, "require_personal_api_key", "false")
        require_personal_key = require_setting.lower() == "true"
    
    # If personal API key is required but not provided, return appropriate message
    if require_personal_key and not user_api_key:
        # Detect language for appropriate error message
        def detect_language(text: str) -> str:
            arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
            english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
            total_chars = arabic_chars + english_chars
            
            if total_chars == 0:
                return "english"
            
            arabic_ratio = arabic_chars / total_chars
            return "arabic" if arabic_ratio > 0.3 else "english"
        
        user_language = detect_language(prompt)
        
        if user_language == "arabic":
            error_message = get_ai_setting(db, "api_key_required_message_arabic", 
                "للاستفادة من خدمة الذكاء الاصطناعي، يجب عليك إضافة مفتاح API الخاص بك في صفحة الملف الشخصي.")
        else:
            error_message = get_ai_setting(db, "api_key_required_message_english", 
                "To use AI features, please add your personal API key in your Profile settings.")
        
        raise ValueError(error_message)
    
    # Use user's personal API key if provided
    if user_api_key:
        api_url = settings.GROQ_API_URL
        api_key = user_api_key
        print(f"🔑 Using user's personal Groq API key")
    # Get system API key from database if no user key provided
    elif db:
        system_api_key = get_ai_setting(db, "system_groq_api_key")
        if system_api_key and system_api_key != "your_groq_api_key_here":
            api_url = settings.GROQ_API_URL
            api_key = system_api_key
            print(f"🔑 Using system Groq API key from database")
        else:
            raise ValueError("No valid Groq API key found in database")
    # Fallback to environment variables
    elif settings.AI_PROVIDER == "groq":
        api_url = settings.GROQ_API_URL
        api_key = settings.GROQ_API_KEY
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY not configured in environment")
        print(f"🚀 Using Groq API from environment with model: {settings.AI_MODEL}")
    elif settings.AI_PROVIDER == "deepseek":
        api_url = settings.DEEPSEEK_API_URL
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        print(f"🤖 Using DeepSeek API with model: {settings.AI_MODEL}")
    else:
        api_url = settings.OPENROUTER_API_URL
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        print(f"🤖 Using OpenRouter API with model: {settings.AI_MODEL}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": settings.AI_MODEL,
        "messages": messages
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
        if e.response.status_code == 429:
            # Rate limit hit - return a helpful mock response
            print("⚠️ Rate limit hit (429). Using mock response for testing.")
            if "resume" in prompt.lower() or "analyze" in prompt.lower():
                # Mock resume analysis
                return """```json
{
  "skills": [
    {"name": "Python", "category": "technical"},
    {"name": "FastAPI", "category": "technical"},
    {"name": "React", "category": "technical"}
  ],
  "work_experience": [
    {
      "company": "Tech Corp",
      "title": "Software Developer",
      "start_date": "2020-01",
      "end_date": "2023-12",
      "description": "Developed web applications"
    }
  ],
  "education": [
    {
      "institution": "University",
      "degree": "Bachelor",
      "field": "Computer Science",
      "graduation_date": "2020"
    }
  ],
  "summary": "Experienced developer with expertise in Python and web technologies. [MOCK DATA - API Rate Limited]"
}
```"""
            else:
                # Mock chat response - try to be helpful even when rate limited
                return "Based on the database query, here are the relevant candidates matching your criteria. (Note: AI service is rate-limited, detailed analysis temporarily unavailable. Try again in a few minutes for full AI responses.)"
        raise
    except Exception as e:
        print(f"❌ Unexpected Error calling AI API: {type(e).__name__}: {str(e)}")
        raise


def get_ai_setting(db: Session, setting_key: str, default_value: str = None) -> str:
    """
    Get AI setting from database, return default if not found
    """
    try:
        # Import here to avoid circular imports
        from app.db.models_users import SystemSettings
        
        setting = db.query(SystemSettings).filter(
            SystemSettings.key == setting_key
        ).first()
        
        if setting and setting.value:
            return setting.value
        return default_value or ""
    except Exception as e:
        print(f"⚠️ Error fetching AI setting '{setting_key}': {e}")
        return default_value or ""


def safe_extract_string(data: dict, key: str, default: str = "") -> str:
    """
    Safely extract a string value from dictionary, handling nulls and type mismatches
    """
    try:
        value = data.get(key, default)
        if value is None:
            return default
        if isinstance(value, list):
            # If it's a list, take first non-empty item
            value = next((str(v).strip() for v in value if v and str(v).strip()), default)
        elif not isinstance(value, str):
            value = str(value)
        return value.strip() if value else default
    except Exception as e:
        print(f"⚠️ Error extracting '{key}': {e}")
        return default


def clean_email_address(email_string: str) -> str:
    """
    Clean email address by taking the first valid email if multiple are present
    """
    try:
        if not email_string or not isinstance(email_string, str):
            return ""
        
        # Split by common delimiters used for multiple emails
        email_string = email_string.strip()
        
        # Check for multiple emails separated by comma, semicolon, or space
        delimiters = [',', ';', ' ', '\n', '\t']
        for delimiter in delimiters:
            if delimiter in email_string:
                emails = email_string.split(delimiter)
                # Take the first non-empty email that contains @
                for email in emails:
                    email = email.strip()
                    if email and '@' in email and '.' in email:
                        # Basic email validation
                        if not any(char in email for char in [',', ';', ' '] if char != delimiter):
                            return email
        
        # If no delimiters found, return the original (might be a single email)
        if '@' in email_string and '.' in email_string:
            return email_string
            
        return ""
    except Exception as e:
        print(f"⚠️ Error cleaning email: {e}")
        return ""


def safe_extract_list(data: dict, key: str, default: list = None) -> list:
    """
    Safely extract a list value from dictionary, handling nulls and type mismatches
    """
    try:
        value = data.get(key, default or [])
        if value is None:
            return default or []
        if not isinstance(value, list):
            # If it's a single value, wrap in list
            return [value] if value else (default or [])
        # Filter out None and empty values
        return [v for v in value if v is not None and (not isinstance(v, str) or v.strip())]
    except Exception as e:
        print(f"⚠️ Error extracting list '{key}': {e}")
        return default or []


def safe_parse_date(date_value, field_name: str = "date") -> datetime.date:
    """
    Safely parse date from various formats, return None if invalid
    """
    if not date_value:
        return None
    
    try:
        date_str = safe_extract_string({"val": date_value}, "val", "")
        if not date_str or date_str.lower() in ["present", "current", "now"]:
            return None
        
        date_str = date_str.strip()
        
        # Try different date formats
        if len(date_str) == 4:  # Just year (YYYY)
            return datetime.strptime(f"{date_str}-01-01", "%Y-%m-%d").date()
        elif len(date_str) == 7:  # YYYY-MM
            return datetime.strptime(f"{date_str}-01", "%Y-%m-%d").date()
        elif len(date_str) == 10:  # YYYY-MM-DD
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            # Try parsing as full date
            return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, AttributeError, TypeError) as e:
        print(f"⚠️ Could not parse {field_name}: {date_value} - {e}")
        return None


async def analyze_resume(text: str, candidate_id: str, db: Session, current_user = None) -> Dict[str, Any]:
    """
    Analyze resume text using AI to extract structured information
    """
    # Get user's personal API key if configured
    user_api_key = None
    if current_user and hasattr(current_user, 'use_personal_ai_key') and current_user.use_personal_ai_key:
        user_api_key = getattr(current_user, 'personal_groq_api_key', None)
    
    # Get custom instructions - user's custom instructions take priority
    custom_instructions = None
    if (current_user and 
        getattr(current_user, 'use_custom_instructions', False) and 
        getattr(current_user, 'custom_cv_analysis_instructions', None)):
        
        custom_instructions = current_user.custom_cv_analysis_instructions
        print(f"✨ Using user custom CV analysis instructions")
    else:
        # Fallback to system instructions from database (customizable by admin)
        custom_instructions = get_ai_setting(
            db, 
            "ai_resume_analysis_instructions",
            default_value="AI resume analysis assistant"
        )
        print(f"🔧 Using system CV analysis instructions")
    
    # Use the configurable instructions as the system message
    system_message = custom_instructions + """

Expected JSON output format:
{
  "first_name": "John",
  "last_name": "Doe Smith",
  "email": "john.doe@email.com",
  "phone": "+1-234-567-8900",
  "location": "City, State, Country",
  "linkedin": "linkedin.com/in/johndoe",
  "github": "github.com/johndoe",
  "portfolio": "johndoe.com",
  "summary": "Comprehensive professional summary highlighting key achievements, years of experience, and areas of expertise. Make this 2-3 sentences.",
  "career_level": "Mid",
  "years_of_experience": 5,
  
  "skills": [
    {"name": "Python", "category": "technical", "level": "Expert"},
    {"name": "JavaScript", "category": "technical", "level": "Advanced"},
    {"name": "Project Management", "category": "soft", "level": "Intermediate"},
    {"name": "Healthcare Domain", "category": "domain"}
  ],
  
  "work_experience": [
    {
      "company": "Company Name Inc.", 
      "title": "Senior Software Engineer", 
      "start_date": "2020-01",
      "end_date": "2024-06",
      "description": "• Led development of microservices architecture using Python, Docker, and Kubernetes\n• Mentored team of 5 junior developers, conducting code reviews and technical guidance\n• Improved system performance by 40% through optimization and caching strategies\n• Implemented CI/CD pipelines using Jenkins and GitLab, reducing deployment time by 60%\n• Collaborated with product managers and designers on feature requirements and specifications\n• Managed database migrations and schema updates for PostgreSQL production systems\n• Conducted technical interviews and participated in hiring decisions for engineering team",
      "is_current": false,
      "location": "City, Country",
      "achievements": ["Led successful migration to microservices", "Reduced system downtime by 85%", "Mentored 5 developers to promotion"]
    }
  ],
  
  "education": [
    {
      "institution": "University Name",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "start_date": "2015",
      "graduation_date": "2019-06",
      "grade": "3.8 GPA",
      "achievements": ["Dean's List", "Honor Society"]
    }
  ],
  
  "projects": [
    {
      "name": "E-commerce Platform",
      "type": "Professional",
      "description": "Built scalable e-commerce platform serving 100K+ users",
      "technologies": ["React", "Node.js", "PostgreSQL", "AWS"],
      "url": "github.com/user/project",
      "role": "Lead Developer",
      "start_date": "2023-01",
      "end_date": "2023-12"
    }
  ],
  
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuing_organization": "Amazon Web Services",
      "issue_date": "2023-06",
      "expiry_date": "2026-06",
      "credential_id": "ABC123"
    }
  ],
  
  "languages": [
    {
      "name": "English",
      "proficiency": "Native"
    },
    {
      "name": "Spanish", 
      "proficiency": "Professional"
    }
  ]
}

CRITICAL INSTRUCTIONS FOR DATES:
- Always extract start_date and end_date for work experience
- Use format "YYYY-MM" (e.g., "2020-01") or "YYYY" if only year available
- For current positions: end_date = "Present" and is_current = true
- For education: Extract graduation_date (when they completed) and start_date if available
- For certifications: Extract issue_date and expiry_date if available

IMPORTANT:
- Be thorough - extract ALL information present in the resume
- For work experience descriptions: Include DETAILED responsibilities, daily tasks, technologies used, and specific achievements with metrics
- Don't make up information - only extract what's actually in the resume
- If a field is not found, omit it (don't use null or empty strings)
- For job descriptions: Use bullet points (•) to separate different responsibilities and achievements
- Extract specific technologies, programming languages, frameworks, and tools mentioned
- Include quantifiable results (percentages, numbers, team sizes, revenue impact, etc.)

Return ONLY valid JSON, no additional text or markdown formatting."""
    
    prompt = f"""Analyze this resume and extract structured information:

{text}

Return the analysis as JSON."""
    
    try:
        response = await call_ai_api(prompt, system_message, user_api_key, db)
        
        # Ensure response is a string
        if not isinstance(response, str):
            print(f"⚠️ Unexpected response type: {type(response)}")
            if isinstance(response, list):
                response = str(response[0]) if response else "{}"
            else:
                response = str(response)
        
        # Try to parse JSON from response
        # Sometimes AI adds markdown formatting, so clean it
        json_text = response.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.startswith("```"):
            json_text = json_text[3:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        json_text = json_text.strip()
        
        analysis = json.loads(json_text)
        
        # Validate that analysis has some data
        if not analysis or not isinstance(analysis, dict):
            print("⚠️ Invalid or empty analysis result")
            return {"error": "Failed to extract valid data from resume"}
        
        # Create candidate if candidate_id is None (new resume upload)
        if candidate_id is None:
            # Extract name from analysis with safe extraction - try multiple approaches
            first_name = safe_extract_string(analysis, "first_name", "")
            last_name = safe_extract_string(analysis, "last_name", "")
            
            # If first_name is empty, try to extract from the original text
            if not first_name or first_name == "Unknown":
                # Try to extract name from the original CV text
                lines = text.split('\n')
                for line in lines[:10]:  # Check first 10 lines
                    line = line.strip()
                    if line and len(line.split()) <= 4 and len(line) > 3:
                        # Looks like a name line
                        words = line.split()
                        if len(words) >= 2:
                            potential_first = words[0]
                            potential_last = ' '.join(words[1:])
                            # Check if it looks like a name (not email, phone, etc.)
                            if not any(char in potential_first.lower() for char in ['@', '.com', '+', '(', ')']):
                                first_name = potential_first
                                last_name = potential_last
                                print(f"📝 Extracted name from text: {first_name} {last_name}")
                                break
            
            # Final fallback
            if not first_name:
                first_name = "Candidate"
            
            raw_email = safe_extract_string(analysis, "email", f"temp_{datetime.utcnow().timestamp()}@temp.com")
            
            # Clean email address to handle multiple emails
            email = clean_email_address(raw_email)
            
            # Validate email format - if it looks invalid, use temp email
            if not email or "@" not in email or email.startswith("temp_"):
                email = f"temp_{datetime.utcnow().timestamp()}@temp.com"
            
            # Check if candidate already exists by email
            existing_candidate = None
            if email and isinstance(email, str) and not email.startswith("temp_"):
                existing_candidate = db.query(models.Candidate).filter(models.Candidate.email == email).first()
            
            if existing_candidate:
                # Update existing candidate with new information
                print(f"📧 Found existing candidate with email {email}, updating...")
                candidate_id = existing_candidate.id
                
                # Update candidate info with new data from resume (only if not empty/None)
                if first_name and first_name != "Unknown":
                    existing_candidate.first_name = first_name
                if last_name:
                    existing_candidate.last_name = last_name
                
                phone = safe_extract_string(analysis, "phone")
                if phone:
                    existing_candidate.phone = phone
                
                location = safe_extract_string(analysis, "location")
                if location:
                    existing_candidate.current_location = location
                
                summary = safe_extract_string(analysis, "summary")
                if summary:
                    existing_candidate.professional_summary = summary
                
                career_level = safe_extract_string(analysis, "career_level")
                if career_level:
                    existing_candidate.career_level = career_level
                
                years_exp = analysis.get("years_of_experience")
                if years_exp and isinstance(years_exp, int):
                    existing_candidate.years_of_experience = years_exp
                
                linkedin = safe_extract_string(analysis, "linkedin")
                if linkedin:
                    existing_candidate.linkedin_url = linkedin
                
                github = safe_extract_string(analysis, "github")
                if github:
                    existing_candidate.github_url = github
                
                portfolio = safe_extract_string(analysis, "portfolio")
                if portfolio:
                    existing_candidate.portfolio_url = portfolio
                
                existing_candidate.updated_at = datetime.utcnow()
                
                # Delete old data to replace with fresh analysis
                db.query(models.Skill).filter(models.Skill.candidate_id == candidate_id).delete()
                db.query(models.WorkExperience).filter(models.WorkExperience.candidate_id == candidate_id).delete()
                db.query(models.Education).filter(models.Education.candidate_id == candidate_id).delete()
                db.query(models.Project).filter(models.Project.candidate_id == candidate_id).delete()
                db.query(models.Certification).filter(models.Certification.candidate_id == candidate_id).delete()
                
            else:
                # Create new candidate
                print(f"✨ Creating new candidate: {first_name} {last_name}")
                candidate = models.Candidate(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=safe_extract_string(analysis, "phone", None),
                    current_location=safe_extract_string(analysis, "location", None),
                    professional_summary=safe_extract_string(analysis, "summary", None),
                    career_level=safe_extract_string(analysis, "career_level", None),
                    years_of_experience=analysis.get("years_of_experience", 0) if isinstance(analysis.get("years_of_experience"), int) else 0,
                    linkedin_url=safe_extract_string(analysis, "linkedin", None),
                    github_url=safe_extract_string(analysis, "github", None),
                    portfolio_url=safe_extract_string(analysis, "portfolio", None)
                )
                db.add(candidate)
                db.flush()  # Get the ID
                candidate_id = candidate.id
        
        # Store extracted skills in database
        skills_list = safe_extract_list(analysis, "skills")
        if skills_list:
            for skill_data in skills_list:
                try:
                    # Extract skill name - handle both dict and string formats
                    if isinstance(skill_data, dict):
                        skill_name = safe_extract_string(skill_data, "name") or \
                                    safe_extract_string(skill_data, "skill_name") or \
                                    safe_extract_string(skill_data, "skill")
                        category = safe_extract_string(skill_data, "category", "technical")
                        level = safe_extract_string(skill_data, "level", None)
                    else:
                        skill_name = str(skill_data).strip() if skill_data else ""
                        category = "technical"
                        level = None
                    
                    # Skip if no skill name
                    if not skill_name or skill_name.strip() == "":
                        continue
                    
                    # Create skill directly linked to candidate
                    skill = models.Skill(
                        candidate_id=candidate_id,
                        skill_name=skill_name.strip(),
                        skill_category=category,
                        proficiency_level=level
                    )
                    db.add(skill)
                except Exception as e:
                    print(f"⚠️ Error processing skill: {skill_data} - {e}")
                    continue
        
        # Store work experience
        work_exp_list = safe_extract_list(analysis, "work_experience")
        if work_exp_list:
            for exp in work_exp_list:
                try:
                    if not isinstance(exp, dict):
                        print(f"⚠️ Invalid work experience format: {exp}")
                        continue
                    
                    # Parse dates using safe date parser
                    start_date = safe_parse_date(exp.get("start_date"), "work start_date")
                    end_date = safe_parse_date(exp.get("end_date"), "work end_date")
                    
                    # Extract fields safely
                    company_name = safe_extract_string(exp, "company", "Unknown Company")
                    job_title = safe_extract_string(exp, "title", "Unknown Position")
                    description = safe_extract_string(exp, "description", "")
                    location = safe_extract_string(exp, "location", None)
                    is_current = bool(exp.get("is_current", False))
                    achievements = safe_extract_list(exp, "achievements")
                    
                    # Calculate duration in months for this role
                    duration_months = 0
                    if start_date:
                        if end_date:
                            # Calculate difference between start and end date
                            delta = end_date - start_date
                            duration_months = round(delta.days / 30.44, 1)  # Average days per month
                        elif is_current:
                            # Calculate from start date to now
                            delta = datetime.utcnow().date() - start_date
                            duration_months = round(delta.days / 30.44, 1)
                    
                    # Ensure minimum value and reasonable maximum
                    if duration_months < 0:
                        duration_months = 0
                    elif duration_months > 600:  # Sanity check (50 years)
                        duration_months = 600
                    
                    work_exp = models.WorkExperience(
                        candidate_id=candidate_id,
                        company_name=company_name,
                        job_title=job_title,
                        responsibilities=description,
                        start_date=start_date,
                        end_date=end_date,
                        is_current=is_current,
                        company_location=location,
                        achievements=achievements if achievements else None,
                        duration_months=int(duration_months) if duration_months > 0 else None
                    )
                    db.add(work_exp)
                except Exception as e:
                    print(f"⚠️ Error processing work experience: {exp} - {e}")
                    continue
        
        # Store education
        education_list = safe_extract_list(analysis, "education")
        if education_list:
            for edu in education_list:
                try:
                    if not isinstance(edu, dict):
                        print(f"⚠️ Invalid education format: {edu}")
                        continue
                    
                    # Parse dates using safe date parser
                    start_date = safe_parse_date(edu.get("start_date"), "education start_date")
                    grad_date = safe_parse_date(edu.get("graduation_date") or edu.get("end_date"), "graduation_date")
                    
                    # Extract graduation year from date
                    graduation_year = None
                    if grad_date:
                        graduation_year = grad_date.year
                    
                    # Extract fields safely
                    institution = safe_extract_string(edu, "institution", "Unknown Institution")
                    degree = safe_extract_string(edu, "degree", "")
                    field = safe_extract_string(edu, "field", "")
                    
                    education = models.Education(
                        candidate_id=candidate_id,
                        institution=institution,
                        degree=degree,
                        field_of_study=field,
                        start_date=start_date,
                        end_date=grad_date,
                        graduation_year=graduation_year
                    )
                    db.add(education)
                except Exception as e:
                    print(f"⚠️ Error processing education: {edu} - {e}")
                    continue
        
        # Store projects
        projects_list = safe_extract_list(analysis, "projects")
        if projects_list:
            for proj in projects_list:
                try:
                    if not isinstance(proj, dict):
                        print(f"⚠️ Invalid project format: {proj}")
                        continue
                    
                    # Parse project dates using safe parser
                    start_date = safe_parse_date(proj.get("start_date"), "project start_date")
                    end_date = safe_parse_date(proj.get("end_date"), "project end_date")
                    
                    # Extract fields safely
                    project_name = safe_extract_string(proj, "name", "Untitled Project")
                    project_type = safe_extract_string(proj, "type", "Professional")
                    description = safe_extract_string(proj, "description", "")
                    role = safe_extract_string(proj, "role", "")
                    technologies = safe_extract_list(proj, "technologies")
                    url = safe_extract_string(proj, "url", "")
                    
                    project = models.Project(
                        candidate_id=candidate_id,
                        project_name=project_name,
                        project_type=project_type,
                        description=description,
                        role=role,
                        technologies_used=technologies,
                        start_date=start_date,
                        end_date=end_date,
                        project_url=url
                    )
                    db.add(project)
                except Exception as e:
                    print(f"⚠️ Error processing project: {proj} - {e}")
                    continue
        
        # Store certifications
        certifications_list = safe_extract_list(analysis, "certifications")
        if certifications_list:
            for cert in certifications_list:
                try:
                    if not isinstance(cert, dict):
                        print(f"⚠️ Invalid certification format: {cert}")
                        continue
                    
                    # Parse dates using safe parser
                    issue_date = safe_parse_date(cert.get("issue_date"), "cert issue_date")
                    expiry_date = safe_parse_date(cert.get("expiry_date"), "cert expiry_date")
                    
                    # Extract fields safely
                    cert_name = safe_extract_string(cert, "name") or safe_extract_string(cert, "certification_name", "Unknown Certification")
                    issuing_org = safe_extract_string(cert, "issuing_organization", "")
                    credential_id = safe_extract_string(cert, "credential_id", None)
                    credential_url = safe_extract_string(cert, "credential_url", None)
                    
                    certification = models.Certification(
                        candidate_id=candidate_id,
                        certification_name=cert_name,
                        issuing_organization=issuing_org,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        credential_id=credential_id,
                        credential_url=credential_url
                    )
                    db.add(certification)
                except Exception as e:
                    print(f"⚠️ Error processing certification: {cert} - {e}")
                    continue
        
        # Store languages
        languages_list = safe_extract_list(analysis, "languages")
        if languages_list:
            for lang in languages_list:
                try:
                    if isinstance(lang, dict):
                        lang_name = safe_extract_string(lang, "name", "")
                        proficiency = safe_extract_string(lang, "proficiency", "")
                    else:
                        lang_name = str(lang).strip() if lang else ""
                        proficiency = ""
                    
                    if not lang_name:
                        continue
                    
                    language = models.Language(
                        candidate_id=candidate_id,
                        language_name=lang_name,
                        proficiency_level=proficiency
                    )
                    db.add(language)
                except Exception as e:
                    print(f"⚠️ Error processing language: {lang} - {e}")
                    continue
        
        db.commit()
        
        # Return analysis with candidate_id
        analysis['candidate_id'] = str(candidate_id)
        return analysis
        
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        return {"error": str(e)}


async def chat_with_database(query: str, db: Session, current_user = None, conversation_history: list = None) -> Dict[str, Any]:
    """
    Natural language chat interface to query the database using AI
    Supports conversation history for context-aware responses
    Includes candidates, jobs, and applications context
    """
    # Log user activity for audit trail
    user_identifier = "anonymous"
    if current_user:
        user_identifier = getattr(current_user, 'email', getattr(current_user, 'id', 'unknown'))
        print(f"👤 Chat request from user: {user_identifier}")
    
    # Get user's personal API key if configured
    user_api_key = None
    if current_user and hasattr(current_user, 'use_personal_ai_key') and current_user.use_personal_ai_key:
        user_api_key = getattr(current_user, 'personal_groq_api_key', None)
    
    # Detect if query is candidate/HR related or general chat
    query_lower = query.lower()
    
    # HR/Candidate related keywords
    hr_keywords = [
        'candidate', 'candidates', 'resume', 'cv', 'job', 'position', 'skill', 'experience', 
        'developer', 'engineer', 'manager', 'hire', 'recruit', 'interview', 'apply', 'application',
        'مرشح', 'مرشحين', 'سيرة', 'وظيفة', 'مهارة', 'خبرة', 'مطور', 'مهندس', 'توظيف', 'مقابلة'
    ]
    
    # Check if any HR keywords are in the query or if specific names are mentioned
    is_hr_related = any(keyword in query_lower for keyword in hr_keywords)
    
    # Also check if specific candidate names are mentioned
    all_candidates = db.query(models.Candidate).all()
    mentioned_candidates = []
    
    for candidate in all_candidates:
        full_name = f"{candidate.first_name} {candidate.last_name}".lower()
        first_name = candidate.first_name.lower()
        last_name = candidate.last_name.lower()
        
        if (first_name in query_lower or 
            last_name in query_lower or 
            full_name in query_lower):
            mentioned_candidates.append(candidate)
            is_hr_related = True
    
    print(f"🔍 Chat query: {query}")
    print(f"🎯 HR-related query: {is_hr_related}")
    
    # If it's not HR-related, provide a simple conversational response
    if not is_hr_related:
        # Detect language preference from query
        def detect_language(text: str) -> str:
            arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
            english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
            total_chars = arabic_chars + english_chars
            
            if total_chars == 0:
                return "english"
            
            arabic_ratio = arabic_chars / total_chars
            return "arabic" if arabic_ratio > 0.3 else "english"
        
        user_language = detect_language(query)
        print(f"🌐 Detected language: {user_language}")
        
        # Get user's custom instructions if enabled
        chat_instructions = None
        if (current_user and 
            getattr(current_user, 'use_custom_instructions', False) and 
            getattr(current_user, 'custom_chat_instructions', None)):
            
            chat_instructions = current_user.custom_chat_instructions
            print(f"✨ Using user custom chat instructions")
        else:
            # Fallback to system chat instructions
            chat_instructions = get_ai_setting(db, "ai_chat_instructions", 
                                              default_value="AI HR assistant")
            print(f"🔧 Using system chat instructions")
        
        # Get language-specific AI instructions from database
        if user_language == "arabic":
            setting_key = "ai_instructions_arabic"
            default_instructions = get_ai_setting(db, setting_key, 
                default_value="مساعد ذكي")
        else:
            setting_key = "ai_instructions_english" 
            default_instructions = get_ai_setting(db, setting_key,
                default_value="AI assistant")
        
        custom_instructions = default_instructions
        
        # Get language enforcement instruction from settings
        if user_language == "arabic":
            language_instruction = get_ai_setting(db, "ai_language_enforcement_arabic", 
                default_value="استخدم العربية فقط")
        else:
            language_instruction = get_ai_setting(db, "ai_language_enforcement_english", 
                default_value="Use English only")
        
        simple_prompt = f"""Current Question: {query}

{chat_instructions}

{language_instruction}

Language: {"Arabic" if user_language == "arabic" else "English"}

Answer the question directly and professionally."""

        try:
            ai_response = await call_ai_api(simple_prompt, custom_instructions, user_api_key, db)
            return {
                "response": ai_response,
                "candidates": [],
                "jobs": []
            }
        except Exception as e:
            print(f"❌ AI API Error: {e}")
            # Get fallback response from settings
            fallback_response = get_ai_setting(db, f"ai_fallback_response_{user_language}", 
                                             default_value="Service unavailable" if user_language == "english" 
                                             else "الخدمة غير متاحة")
            return {
                "response": fallback_response,
                "candidates": [],
                "jobs": []
            }
    
    # Continue with HR-related logic for candidate queries
    candidates = mentioned_candidates if mentioned_candidates else all_candidates
    
    print(f"📊 Found {len(candidates)} relevant candidates:")
    for c in candidates:
        print(f"   - {c.first_name} {c.last_name}")

    # Detect language preference from query
    def detect_language(text: str) -> str:
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
        total_chars = arabic_chars + english_chars
        
        if total_chars == 0:
            return "english"  # Default to English if no clear language detected
        
        arabic_ratio = arabic_chars / total_chars
        return "arabic" if arabic_ratio > 0.3 else "english"
    
    user_language = detect_language(query)
    print(f"🌐 Detected language: {user_language}")

    # Build comprehensive context about candidates
    context_parts = []
    candidate_ids = []
    
    for candidate in candidates:
        candidate_ids.append(str(candidate.id))
        
        # Get skills
        skills = []
        for skill in candidate.skills:
            skill_name = skill.skill_name if skill.skill_name else "Unknown"
            skills.append(skill_name)
        
        # Get work experience
        work_exp = []
        for exp in candidate.work_experiences:
            work_exp.append({
                "title": exp.job_title,
                "company": exp.company_name,
                "description": exp.responsibilities or "",
                "current": exp.is_current
            })
        
        # Get education
        education = []
        for edu in candidate.educations:
            education.append({
                "degree": edu.degree,
                "institution": edu.institution,
                "field": edu.field_of_study
            })
        
        # Build candidate summary
        candidate_info = f"""
Candidate: {candidate.first_name} {candidate.last_name}
Email: {candidate.email}
Location: {candidate.current_location or 'Not specified'}
Years of Experience: {candidate.years_of_experience or 0} years
Career Level: {candidate.career_level or 'Not specified'}
Summary: {candidate.professional_summary or 'No summary available'}

Skills: {', '.join(skills) if skills else 'No skills listed'}

Work Experience:
"""
        for i, exp in enumerate(work_exp, 1):
            status = "(Current)" if exp.get("current") else ""
            candidate_info += f"{i}. {exp['title']} at {exp['company']} {status}\n"
            if exp.get("description"):
                candidate_info += f"   {exp['description'][:200]}...\n"
        
        if education:
            candidate_info += "\nEducation:\n"
            for edu in education:
                candidate_info += f"- {edu['degree']} in {edu['field']} from {edu['institution']}\n"
        
        context_parts.append(candidate_info)
    
    database_context = "\n---\n".join(context_parts)
    
    # Enhanced jobs context - Always include if query mentions positions or is about matching
    jobs_context = ""
    job_related_terms = ['job', 'position', 'opening', 'vacancy', 'suitable', 'best', 'match', 'fit', 'recommend', 
                        'وظيفة', 'وظائف', 'منصب', 'مناسب', 'أفضل', 'يناسب', 'ملائم', 'أنسب', 'الأنسب']
    
    if any(word in query_lower for word in job_related_terms):
        jobs = db.query(models.Job).filter(models.Job.status == 'open').limit(10).all()
        if jobs:
            if user_language == "arabic":
                jobs_context = "\n\nالوظائف المتاحة:\n"
            else:
                jobs_context = "\n\nAVAILABLE JOBS:\n"
                
            for job in jobs:
                required_skills_str = ', '.join(job.required_skills or [])
                if user_language == "arabic":
                    jobs_context += f"""
الوظيفة: {job.title}
الموقع: {job.location or 'عن بُعد'}
النوع: {job.employment_type or 'دوام كامل'}
المهارات المطلوبة: {required_skills_str}
سنوات الخبرة: {job.min_experience_years or 0}-{job.max_experience_years or 10} سنة
الراتب: {job.salary_min}-{job.salary_max} {job.salary_currency or 'USD'}
الوصف: {job.description[:200] if job.description else 'غير محدد'}...
---"""
                else:
                    jobs_context += f"""
Job: {job.title}
Location: {job.location or 'Remote'}
Type: {job.employment_type or 'Full-time'}
Required Skills: {required_skills_str}
Experience: {job.min_experience_years or 0}-{job.max_experience_years or 10} years
Salary: {job.salary_min}-{job.salary_max} {job.salary_currency or 'USD'}
Description: {job.description[:200] if job.description else 'Not specified'}...
---"""
        else:
            # No jobs available - inform the AI
            if user_language == "arabic":
                jobs_context = "\n\nملاحظة: لا توجد وظائف متاحة حالياً في النظام. يرجى تقييم المرشحين بناءً على المؤهلات العامة.\n"
            else:
                jobs_context = "\n\nNote: No active job openings are currently available in the system. Please evaluate candidates based on general qualifications.\n"
    
    # Add Applications context if query mentions applications/candidates applying
    applications_context = ""
    if any(word in query_lower for word in ['application', 'applied', 'applying', 'candidate', 'تقديم', 'متقدم']):
        applications = db.query(models.Application).limit(50).all()
        if applications:
            applications_context = "\n\nAPPLICATIONS STATUS:\n"
            for app in applications:
                candidate = db.query(models.Candidate).filter(models.Candidate.id == app.candidate_id).first()
                job = db.query(models.Job).filter(models.Job.id == app.job_id).first()
                if candidate and job:
                    applications_context += f"""
- {candidate.first_name} {candidate.last_name} applied for {job.title}
  Status: {app.status}, Stage: {app.current_stage or 'Initial'}
---"""
    
    # Detect language preference from query
    def detect_language(text: str) -> str:
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
        total_chars = arabic_chars + english_chars
        
        if total_chars == 0:
            return "english"  # Default to English if no clear language detected
        
        arabic_ratio = arabic_chars / total_chars
        return "arabic" if arabic_ratio > 0.3 else "english"
    
    user_language = detect_language(query)
    
    # Get language-specific AI instructions from database (customizable by admin)
    if user_language == "arabic":
        setting_key = "ai_instructions_arabic"
        default_instructions = get_ai_setting(db, setting_key, 
            default_value="مساعد ذكي")
    else:
        setting_key = "ai_instructions_english"
        default_instructions = get_ai_setting(db, setting_key,
            default_value="AI assistant")
    
    # Get HR-specific context instructions
    hr_context_instructions = get_ai_setting(db, "ai_hr_context_instructions",
        default_value="HR assistant")
    
    custom_instructions = get_ai_setting(
        db,
        setting_key,
        default_value=default_instructions
    )
    
    system_message = custom_instructions + """
    
CURRENT DATABASE CONTEXT:
""" + database_context + jobs_context + applications_context
    
    # Build conversation context if history exists
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\nPREVIOUS CONVERSATION:\n"
        for msg in conversation_history[-6:]:  # Include last 6 messages (3 exchanges) for context
            # Handle both Pydantic objects and dictionaries
            if hasattr(msg, 'role'):
                # Pydantic ChatMessage object
                role = "User" if msg.role == "user" else "Assistant"
                content = msg.content
            else:
                # Dictionary
                role = "User" if msg.get("role") == "user" else "Assistant"
                content = msg.get('content')
            
            conversation_context += f"{role}: {content}\n"
        conversation_context += "\n"

    # Get evaluation format from database settings instead of hard-coding
    evaluation_format = {
        "arabic": get_ai_setting(db, "ai_evaluation_format_arabic", 
                                default_value="قيّم المرشحين بناءً على مؤهلاتهم ومدى ملاءمتهم للوظيفة المطلوبة."),
        "english": get_ai_setting(db, "ai_evaluation_format_english", 
                                 default_value="Evaluate candidates based on their qualifications and job fit.")
    }

    user_prompt = f"""Answer this question about our candidates in a natural, helpful way:
{conversation_context}
Current Question: {query}

{hr_context_instructions}

{evaluation_format.get(user_language, evaluation_format["english"])}

CANDIDATE PROFILES:
{database_context}

{jobs_context}

IMPORTANT: 
- The candidates listed above are the ONLY ones you should discuss. 
- Use their exact names and details from their profiles.
- If a specific job is mentioned, analyze each candidate's fit for that exact position.
- If no specific job is mentioned, ask for clarification about the position requirements.
- If the user asks follow-up questions, refer to the previous conversation context.
- Maintain continuity with previous responses in the conversation.
- {get_ai_setting(db, f"ai_language_enforcement_{user_language}", default_value="Use appropriate language")}
- Provide a structured, professional analysis based on the candidate data and conversation history above."""

    # Call AI to generate response
    try:
        ai_response = await call_ai_api(user_prompt, system_message, user_api_key, db)
        
        # Clean up response if it contains JSON markers or code blocks
        if "```" in ai_response:
            ai_response = ai_response.split("```")[0].strip()
        
        # Parse response to find which candidates were actually mentioned
        mentioned_candidate_ids = []
        response_lower = ai_response.lower()
        
        for candidate in candidates:
            full_name = f"{candidate.first_name} {candidate.last_name}".lower()
            first_name = candidate.first_name.lower()
            last_name = candidate.last_name.lower()
            
            # Check if candidate name appears in the response
            if (full_name in response_lower or 
                first_name in response_lower or 
                last_name in response_lower):
                mentioned_candidate_ids.append(str(candidate.id))
        
        # If no candidates were explicitly mentioned, return empty list
        # This prevents showing unrelated CV download buttons
        return {
            "response": ai_response,
            "candidates": mentioned_candidate_ids,
            "jobs": []
        }
    except Exception as e:
        # Fallback if AI fails
        return {
            "response": f"I found {len(candidates)} candidate(s) in the database. However, I'm having trouble generating a detailed response. Please try rephrasing your question.",
            "candidates": [],  # Don't show candidates on error
            "jobs": []
        }


async def semantic_search(query: str, limit: int, db: Session) -> List[Dict[str, Any]]:
    """
    Perform semantic search for candidates based on job requirements
    This is a simple implementation - can be enhanced with vector embeddings
    """
    try:
        # For now, use keyword-based search as a placeholder
        # In production, this would use vector embeddings
        
        # Extract keywords from query
        keywords = query.lower().split()
        
        # Search for candidates with matching skills
        candidates = db.query(models.Candidate).limit(limit).all()
        
        results = []
        for candidate in candidates:
            # Get candidate skills directly (no CandidateSkill table)
            skill_names = []
            for skill in candidate.skills:
                if skill.skill_name:
                    skill_names.append(skill.skill_name.lower())
            
            # Calculate simple match score
            match_score = sum(1 for keyword in keywords if any(keyword in skill for skill in skill_names))
            
            if match_score > 0:
                results.append({
                    "candidate_id": str(candidate.id),
                    "name": f"{candidate.first_name} {candidate.last_name}",
                    "email": candidate.email,
                    "match_score": match_score * 20,  # Convert to percentage-like score
                    "matched_skills": [s for s in skill_names if any(k in s for k in keywords)]
                })
        
        # Sort by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:limit]
        
    except Exception as e:
        print(f"Error in semantic_search: {str(e)}")
        return []

import httpx
from typing import Dict, Any, List
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import models
from app.db.models_system_settings import SystemAISetting
import json
import re
from datetime import datetime


async def call_ai_api(prompt: str, system_message: str = None, user_api_key: str = None) -> str:
    """
    Call AI API (OpenRouter or DeepSeek) for completions
    Args:
        user_api_key: Optional user's personal API key
    """
    # If USE_MOCK_AI is enabled, skip API and use mock responses
    if settings.USE_MOCK_AI:
        print("🤖 Using mock AI response (USE_MOCK_AI=true)")
        if "resume" in prompt.lower() or "analyze" in prompt.lower():
            return """```json
{
  "skills": [
    {"name": "Python", "category": "technical"},
    {"name": "JavaScript", "category": "technical"},
    {"name": "React", "category": "technical"},
    {"name": "PostgreSQL", "category": "technical"},
    {"name": "Communication", "category": "soft"}
  ],
  "work_experience": [
    {
      "company": "TechCorp Solutions",
      "title": "Senior Software Developer",
      "start_date": "2020-01",
      "end_date": "2024-12",
      "description": "Led development of full-stack web applications using React and FastAPI"
    },
    {
      "company": "StartupXYZ",
      "title": "Junior Developer",
      "start_date": "2018-06",
      "end_date": "2019-12",
      "description": "Developed and maintained web applications"
    }
  ],
  "education": [
    {
      "institution": "Tech University",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "graduation_date": "2018-05"
    }
  ],
  "summary": "Experienced full-stack developer with 6+ years of experience in web development, specializing in Python, React, and PostgreSQL."
}
```"""
        else:
            # For chat queries, extract candidate info from the prompt
            if "Candidate:" in prompt:
                # Parse candidate names from the prompt
                import re
                candidates = re.findall(r'Candidate: ([^\n]+)', prompt)
                if candidates:
                    response = f"I found {len(candidates)} candidate(s) in the database:\n\n"
                    for i, name in enumerate(candidates[:3], 1):
                        response += f"{i}. **{name}**: "
                        if "kareem" in name.lower() and "hassan" in name.lower():
                            response += "Experienced developer with skills in Python, FastAPI, React, JavaScript, PostgreSQL, and Communication. Works at TechCorp Solutions as a Senior Software Developer.\n\n"
                        else:
                            response += "Full-stack developer with strong technical skills and professional experience.\n\n"
                    response += "\n*(Note: This is a mock AI response. For real AI insights, add credit to your DeepSeek account or use a different AI provider)*"
                    return response
            return "Based on the database, I found several candidates. However, I need a real AI connection to provide detailed analysis. Please add credit to your DeepSeek account or configure a different AI provider."
    
    # Use user's personal API key if provided
    if user_api_key:
        api_url = settings.GROQ_API_URL
        api_key = user_api_key
        print(f"🔑 Using user's personal Groq API key")
    # Determine which API to use
    elif settings.AI_PROVIDER == "groq":
        api_url = settings.GROQ_API_URL
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not configured")
        print(f"🚀 Using Groq API with model: {settings.AI_MODEL}")
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
        setting = db.query(SystemAISetting).filter(
            SystemAISetting.setting_key == setting_key,
            SystemAISetting.is_active == True
        ).first()
        
        if setting:
            return setting.setting_value
        return default_value
    except Exception as e:
        print(f"⚠️ Error fetching AI setting '{setting_key}': {e}")
        return default_value


async def analyze_resume(text: str, candidate_id: str, db: Session, current_user = None) -> Dict[str, Any]:
    """
    Analyze resume text using AI to extract structured information
    """
    # Get user's personal API key if configured
    user_api_key = None
    if current_user and hasattr(current_user, 'use_personal_ai_key') and current_user.use_personal_ai_key:
        user_api_key = getattr(current_user, 'personal_groq_api_key', None)
    
    # Get system instructions from database (customizable by admin)
    custom_instructions = get_ai_setting(
        db, 
        "resume_analysis_instructions",
        default_value="""You are an expert HR assistant and resume analyst. 
Extract comprehensive information from the resume text and return it as detailed JSON.

CRITICAL EXTRACTION RULES:
1. Extract COMPLETE names (first, middle, last) - don't truncate
2. Extract FULL email addresses and phone numbers with country codes if present
3. For work experience: Extract ALL positions, with accurate dates and detailed descriptions
4. For skills: Categorize as technical, soft, or domain-specific
5. For education: Include ALL degrees, certifications, and courses
6. Extract projects with technologies used
7. Extract languages with proficiency levels if mentioned"""
    )
    
    system_message = custom_instructions + """
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
      "description": "Led development of microservices architecture. Mentored 5 junior developers. Improved system performance by 40%.",
      "is_current": false,
      "location": "City, Country",
      "achievements": ["Achievement 1", "Achievement 2"]
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
- For work experience descriptions: Include key responsibilities AND achievements
- Don't make up information - only extract what's actually in the resume
- If a field is not found, omit it (don't use null or empty strings)

Return ONLY valid JSON, no additional text or markdown formatting."""
    
    prompt = f"""Analyze this resume and extract structured information:

{text}

Return the analysis as JSON."""
    
    try:
        response = await call_ai_api(prompt, system_message, user_api_key)
        
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
        
        # Create candidate if candidate_id is None (new resume upload)
        if candidate_id is None:
            # Extract name from analysis or use "Unknown"
            first_name = analysis.get("first_name", "Unknown")
            last_name = analysis.get("last_name", "")
            email = analysis.get("email", f"temp_{datetime.utcnow().timestamp()}@temp.com")
            
            # Ensure email is a string
            if isinstance(email, list):
                email = email[0] if email else f"temp_{datetime.utcnow().timestamp()}@temp.com"
            elif not isinstance(email, str):
                email = str(email) if email else f"temp_{datetime.utcnow().timestamp()}@temp.com"
            
            # Check if candidate already exists by email
            existing_candidate = None
            if email and isinstance(email, str) and not email.startswith("temp_"):
                existing_candidate = db.query(models.Candidate).filter(models.Candidate.email == email).first()
            
            if existing_candidate:
                # Update existing candidate with new information
                print(f"📧 Found existing candidate with email {email}, updating...")
                candidate_id = existing_candidate.id
                
                # Update candidate info with new data from resume
                if first_name and first_name != "Unknown":
                    existing_candidate.first_name = first_name
                if last_name:
                    existing_candidate.last_name = last_name
                if analysis.get("phone"):
                    existing_candidate.phone = analysis.get("phone")
                if analysis.get("location"):
                    existing_candidate.current_location = analysis.get("location")
                if analysis.get("summary"):
                    existing_candidate.professional_summary = analysis.get("summary")
                if analysis.get("linkedin"):
                    existing_candidate.linkedin_url = analysis.get("linkedin")
                if analysis.get("github"):
                    existing_candidate.github_url = analysis.get("github")
                if analysis.get("portfolio"):
                    existing_candidate.portfolio_url = analysis.get("portfolio")
                
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
                    phone=analysis.get("phone"),
                    current_location=analysis.get("location"),
                    professional_summary=analysis.get("summary"),
                    linkedin_url=analysis.get("linkedin"),
                    github_url=analysis.get("github"),
                    portfolio_url=analysis.get("portfolio")
                )
                db.add(candidate)
                db.flush()  # Get the ID
                candidate_id = candidate.id
        
        # Store extracted skills in database
        if "skills" in analysis:
            for skill_data in analysis["skills"]:
                # Extract skill name - handle both dict and string formats
                if isinstance(skill_data, dict):
                    skill_name = skill_data.get("name") or skill_data.get("skill_name") or skill_data.get("skill")
                    category = skill_data.get("category", "technical")
                else:
                    skill_name = skill_data
                    category = "technical"
                
                # Skip if no skill name
                if not skill_name or skill_name.strip() == "":
                    continue
                
                # Create skill directly linked to candidate
                skill = models.Skill(
                    candidate_id=candidate_id,
                    skill_name=skill_name.strip(),
                    skill_category=category,
                    proficiency_level=skill_data.get("level") if isinstance(skill_data, dict) else None
                )
                db.add(skill)
        
        # Store work experience
        if "work_experience" in analysis:
            for exp in analysis["work_experience"]:
                # Parse dates - handle various formats
                start_date = None
                end_date = None
                
                # Parse start_date
                if exp.get("start_date"):
                    try:
                        start_str = str(exp.get("start_date")).strip()
                        if len(start_str) == 4:  # Just year
                            start_date = datetime.strptime(f"{start_str}-01-01", "%Y-%m-%d").date()
                        elif len(start_str) == 7:  # YYYY-MM
                            start_date = datetime.strptime(f"{start_str}-01", "%Y-%m-%d").date()
                        else:  # Try full date
                            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                    except (ValueError, AttributeError) as e:
                        print(f"⚠️ Could not parse start_date: {exp.get('start_date')} - {e}")
                
                # Parse end_date
                if exp.get("end_date"):
                    end_str = str(exp.get("end_date")).strip().lower()
                    if end_str not in ["present", "current", "now"]:
                        try:
                            if len(end_str) == 4:  # Just year
                                end_date = datetime.strptime(f"{end_str}-12-31", "%Y-%m-%d").date()
                            elif len(end_str) == 7:  # YYYY-MM
                                end_date = datetime.strptime(f"{end_str}-01", "%Y-%m-%d").date()
                            else:  # Try full date
                                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                        except (ValueError, AttributeError) as e:
                            print(f"⚠️ Could not parse end_date: {exp.get('end_date')} - {e}")
                
                work_exp = models.WorkExperience(
                    candidate_id=candidate_id,
                    company_name=exp.get("company", "Unknown"),
                    job_title=exp.get("title", "Unknown"),
                    responsibilities=exp.get("description", ""),
                    start_date=start_date,
                    end_date=end_date,
                    is_current=exp.get("is_current", False),
                    company_location=exp.get("location"),
                    achievements=exp.get("achievements", []) if exp.get("achievements") else None
                )
                db.add(work_exp)
        
        # Store education
        if "education" in analysis:
            for edu in analysis["education"]:
                # Parse graduation date
                start_date = None
                end_date = None
                graduation_year = None
                
                # Parse start_date
                if edu.get("start_date"):
                    try:
                        start_str = str(edu.get("start_date")).strip()
                        if len(start_str) == 4:  # Just year
                            start_date = datetime.strptime(f"{start_str}-01-01", "%Y-%m-%d").date()
                        elif len(start_str) == 7:  # YYYY-MM
                            start_date = datetime.strptime(f"{start_str}-01", "%Y-%m-%d").date()
                        else:  # Try full date
                            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                    except (ValueError, AttributeError) as e:
                        print(f"⚠️ Could not parse education start_date: {edu.get('start_date')} - {e}")
                
                # Parse graduation_date / end_date
                grad_date_str = edu.get("graduation_date") or edu.get("end_date")
                if grad_date_str:
                    try:
                        grad_str = str(grad_date_str).strip()
                        if len(grad_str) == 4:  # Just year
                            graduation_year = int(grad_str)
                            end_date = datetime.strptime(f"{grad_str}-06-30", "%Y-%m-%d").date()
                        elif len(grad_str) == 7:  # YYYY-MM
                            graduation_year = int(grad_str.split('-')[0])
                            end_date = datetime.strptime(f"{grad_str}-01", "%Y-%m-%d").date()
                        else:  # Try full date
                            end_date = datetime.strptime(grad_str, "%Y-%m-%d").date()
                            graduation_year = end_date.year
                    except (ValueError, AttributeError) as e:
                        print(f"⚠️ Could not parse graduation_date: {grad_date_str} - {e}")
                
                education = models.Education(
                    candidate_id=candidate_id,
                    institution=edu.get("institution", "Unknown"),
                    degree=edu.get("degree", ""),
                    field_of_study=edu.get("field", ""),
                    start_date=start_date,
                    end_date=end_date,
                    graduation_year=graduation_year
                )
                db.add(education)
        
        # Store projects
        if "projects" in analysis:
            for proj in analysis["projects"]:
                # Parse project dates
                start_date = None
                end_date = None
                
                if proj.get("start_date"):
                    try:
                        start_str = str(proj.get("start_date")).strip()
                        if len(start_str) == 4:  # Just year
                            start_date = datetime.strptime(f"{start_str}-01-01", "%Y-%m-%d").date()
                        elif len(start_str) == 7:  # YYYY-MM
                            start_date = datetime.strptime(f"{start_str}-01", "%Y-%m-%d").date()
                        else:
                            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                    except (ValueError, AttributeError):
                        start_date = None
                
                if proj.get("end_date"):
                    try:
                        end_str = str(proj.get("end_date")).strip()
                        if end_str.lower() != "present":
                            if len(end_str) == 4:
                                end_date = datetime.strptime(f"{end_str}-01-01", "%Y-%m-%d").date()
                            elif len(end_str) == 7:
                                end_date = datetime.strptime(f"{end_str}-01", "%Y-%m-%d").date()
                            else:
                                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                    except (ValueError, AttributeError):
                        end_date = None
                
                project = models.Project(
                    candidate_id=candidate_id,
                    project_name=proj.get("name", "Untitled Project"),  # Use project_name instead of title
                    project_type=proj.get("type", "Professional"),
                    description=proj.get("description", ""),
                    role=proj.get("role", ""),
                    technologies_used=proj.get("technologies", []),  # Use technologies_used instead of technologies
                    start_date=start_date,
                    end_date=end_date,
                    project_url=proj.get("url", "")
                )
                db.add(project)
        
        # Store certifications
        if "certifications" in analysis:
            for cert in analysis["certifications"]:
                # Parse issue date
                issue_date = None
                if cert.get("issue_date"):
                    try:
                        issue_str = str(cert.get("issue_date")).strip()
                        if len(issue_str) == 4:  # Just year
                            issue_date = datetime.strptime(f"{issue_str}-01-01", "%Y-%m-%d").date()
                        elif len(issue_str) == 7:  # YYYY-MM
                            issue_date = datetime.strptime(f"{issue_str}-01", "%Y-%m-%d").date()
                        else:  # Try full date
                            issue_date = datetime.strptime(issue_str, "%Y-%m-%d").date()
                    except (ValueError, AttributeError) as e:
                        print(f"⚠️ Could not parse cert issue_date: {cert.get('issue_date')} - {e}")
                
                # Parse expiry date
                expiry_date = None
                if cert.get("expiry_date"):
                    try:
                        expiry_str = str(cert.get("expiry_date")).strip()
                        if len(expiry_str) == 4:  # Just year
                            expiry_date = datetime.strptime(f"{expiry_str}-01-01", "%Y-%m-%d").date()
                        elif len(expiry_str) == 7:  # YYYY-MM
                            expiry_date = datetime.strptime(f"{expiry_str}-01", "%Y-%m-%d").date()
                        else:  # Try full date
                            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    except (ValueError, AttributeError) as e:
                        print(f"⚠️ Could not parse cert expiry_date: {cert.get('expiry_date')} - {e}")
                
                certification = models.Certification(
                    candidate_id=candidate_id,
                    certification_name=cert.get("name", ""),
                    issuing_organization=cert.get("issuing_organization", ""),
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    credential_id=cert.get("credential_id"),
                    credential_url=cert.get("credential_url")
                )
                db.add(certification)
        
        # Store languages
        if "languages" in analysis:
            for lang in analysis["languages"]:
                language = models.Language(
                    candidate_id=candidate_id,
                    language_name=lang.get("name", ""),
                    proficiency_level=lang.get("proficiency", "")
                )
                db.add(language)
        
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
    # Get user's personal API key if configured
    user_api_key = None
    if current_user and hasattr(current_user, 'use_personal_ai_key') and current_user.use_personal_ai_key:
        user_api_key = getattr(current_user, 'personal_groq_api_key', None)
    
    # Smart candidate filtering based on query
    query_lower = query.lower()
    
    # Check if query mentions specific candidate names
    all_candidates = db.query(models.Candidate).all()
    relevant_candidates = []
    
    # If specific names are mentioned, filter to those candidates
    for candidate in all_candidates:
        full_name = f"{candidate.first_name} {candidate.last_name}".lower()
        first_name = candidate.first_name.lower()
        last_name = candidate.last_name.lower()
        
        # Check if candidate name is mentioned in query
        if (first_name in query_lower or 
            last_name in query_lower or 
            full_name in query_lower):
            relevant_candidates.append(candidate)
    
    # If no specific names mentioned, or query asks for "all" or "list", include all candidates
    if not relevant_candidates or any(word in query_lower for word in ['all', 'list', 'show', 'كل', 'جميع']):
        candidates = all_candidates
    else:
        # Use only the relevant candidates mentioned in the query
        candidates = relevant_candidates
    
    # Debug logging
    print(f"🔍 Chat query: {query}")
    print(f"📊 Found {len(candidates)} relevant candidates:")
    for c in candidates:
        print(f"   - {c.first_name} {c.last_name}")
    
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
    
    # Add Jobs context if query mentions jobs/positions
    jobs_context = ""
    if any(word in query_lower for word in ['job', 'position', 'opening', 'vacancy', 'وظيفة', 'وظائف']):
        jobs = db.query(models.Job).filter(models.Job.status == 'open').limit(20).all()
        if jobs:
            jobs_context = "\n\nAVAILABLE JOBS:\n"
            for job in jobs:
                jobs_context += f"""
Job: {job.title}
Location: {job.location or 'Remote'}
Type: {job.employment_type or 'Full-time'}
Required Skills: {', '.join(job.required_skills or [])}
Experience: {job.experience_years_min or 0}-{job.experience_years_max or 10} years
Salary: {job.salary_min}-{job.salary_max} {job.salary_currency or 'USD'}
Description: {job.description[:200] if job.description else 'Not specified'}...
---"""
    
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
    
    # Get custom chat instructions from database
    custom_instructions = get_ai_setting(
        db,
        "chat_system_instructions",
        default_value="""You are a professional HR AI assistant helping recruiters find the best candidates.

IMPORTANT INSTRUCTIONS:
- Give direct, natural, conversational answers based ONLY on the candidate data provided
- ALWAYS use the exact names and information from the profiles below
- Be friendly and helpful
- When comparing candidates, provide specific details
- Support both English and Arabic queries
- Keep answers concise but informative"""
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

    user_prompt = f"""Answer this question about our candidates in a natural, helpful way:
{conversation_context}
Current Question: {query}

CANDIDATE PROFILES:
{database_context}

IMPORTANT: 
- The candidates listed above are the ONLY ones you should discuss. 
- Use their exact names and details from their profiles.
- If the user asks follow-up questions (like "why?", "tell me more", "what about X?"), refer to the previous conversation context.
- Maintain continuity with previous responses in the conversation.
- Provide a natural, helpful answer based on the candidate data and conversation history above."""

    # Call AI to generate response
    try:
        ai_response = await call_ai_api(user_prompt, system_message, user_api_key)
        
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

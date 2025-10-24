import httpx
from typing import Dict, Any, List
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import models
import json
import re
from datetime import datetime


async def call_ai_api(prompt: str, system_message: str = None) -> str:
    """
    Call AI API (OpenRouter or DeepSeek) for completions
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
    
    # Determine which API to use
    if settings.AI_PROVIDER == "groq":
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


async def analyze_resume(text: str, candidate_id: str, db: Session) -> Dict[str, Any]:
    """
    Analyze resume text using AI to extract structured information
    """
    system_message = """You are an expert HR assistant that analyzes resumes. 
    Extract the following information from the resume text and return it as JSON:
    - skills (array of skill names with categories)
    - work_experience (array of jobs with company, title, dates, description)
    - education (array of degrees with institution, degree, field, dates)
    - summary (brief professional summary)
    
    Return ONLY valid JSON, no additional text."""
    
    prompt = f"""Analyze this resume and extract structured information:

{text}

Return the analysis as JSON."""
    
    try:
        response = await call_ai_api(prompt, system_message)
        
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
        
        # Store extracted skills in database
        if "skills" in analysis:
            for skill_data in analysis["skills"]:
                skill_name = skill_data.get("name") if isinstance(skill_data, dict) else skill_data
                category = skill_data.get("category", "technical") if isinstance(skill_data, dict) else "technical"
                
                # Get or create skill
                skill = db.query(models.Skill).filter(
                    models.Skill.name == skill_name
                ).first()
                
                if not skill:
                    skill = models.Skill(name=skill_name, category=category)
                    db.add(skill)
                    db.flush()
                
                # Link to candidate
                candidate_skill = models.CandidateSkill(
                    candidate_id=candidate_id,
                    skill_id=skill.id,
                    source="AI-extracted"
                )
                db.add(candidate_skill)
        
        # Store work experience
        if "work_experience" in analysis:
            for exp in analysis["work_experience"]:
                work_exp = models.WorkExperience(
                    candidate_id=candidate_id,
                    company_name=exp.get("company", "Unknown"),
                    job_title=exp.get("title", "Unknown"),
                    description=exp.get("description", ""),
                    is_current=exp.get("is_current", False)
                )
                db.add(work_exp)
        
        # Store education
        if "education" in analysis:
            for edu in analysis["education"]:
                education = models.Education(
                    candidate_id=candidate_id,
                    institution=edu.get("institution", "Unknown"),
                    degree=edu.get("degree", ""),
                    field_of_study=edu.get("field", "")
                )
                db.add(education)
        
        db.commit()
        return analysis
        
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        return {"error": str(e)}


async def chat_with_database(query: str, db: Session) -> Dict[str, Any]:
    """
    Natural language chat interface to query the database using AI
    """
    # Get all candidates with their related data
    candidates = db.query(models.Candidate).all()
    
    # Build comprehensive context about candidates
    context_parts = []
    candidate_ids = []
    
    for candidate in candidates:
        candidate_ids.append(str(candidate.id))
        
        # Get skills
        skills = []
        for cs in candidate.skills:
            skill_name = cs.skill.name if cs.skill else "Unknown"
            skills.append(skill_name)
        
        # Get work experience
        work_exp = []
        for exp in candidate.work_experiences:
            work_exp.append({
                "title": exp.job_title,
                "company": exp.company_name,
                "description": exp.description or "",
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
Location: {candidate.location or 'Not specified'}
Summary: {candidate.summary or 'No summary available'}

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
    
    # Create AI prompt
    system_message = """You are an AI assistant for an Applicant Tracking System (ATS). 
You help HR professionals find and evaluate candidates by answering questions about the candidate database.

Be conversational, helpful, and provide detailed information when asked.
When asked about what someone can do, describe their skills, experience, and qualifications.
When comparing candidates, highlight their strengths and differences.
When searching, explain why a candidate is a good match.

Keep responses clear, professional, and helpful."""

    user_prompt = f"""Based on the following candidate database, please answer this question:

Question: {query}

Candidate Database:
{database_context}

Please provide a natural, conversational response that directly answers the question using the information available in the database."""

    # Call AI to generate response
    try:
        ai_response = await call_ai_api(user_prompt, system_message)
        
        # Clean up response if it contains JSON markers
        if "```" in ai_response:
            ai_response = ai_response.split("```")[0].strip()
        
        return {
            "response": ai_response,
            "candidates": candidate_ids,
            "jobs": []
        }
    except Exception as e:
        # Fallback if AI fails
        return {
            "response": f"I found {len(candidates)} candidate(s) in the database. However, I'm having trouble generating a detailed response. Please try rephrasing your question.",
            "candidates": candidate_ids,
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
            # Get candidate skills
            candidate_skills = db.query(models.CandidateSkill).filter(
                models.CandidateSkill.candidate_id == candidate.id
            ).all()
            
            skill_names = []
            for cs in candidate_skills:
                skill = db.query(models.Skill).filter(models.Skill.id == cs.skill_id).first()
                if skill:
                    skill_names.append(skill.name.lower())
            
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

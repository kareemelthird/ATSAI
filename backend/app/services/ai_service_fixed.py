import httpx
from typing import Dict, Any, List
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import models
import json
import re


async def call_openrouter_api(prompt: str, system_message: str = None) -> str:
    """
    Call OpenRouter API for AI completions
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
            return "Based on the database query, here are the relevant candidates matching your criteria. (Mock AI response - set USE_MOCK_AI=false in .env to use real AI)"
    
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
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
                settings.OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            # Rate limit hit - return a helpful mock response
            print("⚠️ OpenRouter rate limit hit (429). Using mock response for testing.")
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
                # Mock chat response
                return "I apologize, but the AI service is currently rate-limited. This is a mock response for testing purposes. Please try again in a few minutes when the rate limit resets."
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
        response = await call_openrouter_api(prompt, system_message)
        
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
    Natural language chat interface to query the database
    """
    # Get context about available candidates and jobs
    candidates_count = db.query(models.Candidate).count()
    jobs_count = db.query(models.Job).count()
    
    # Get sample skills for context
    skills = db.query(models.Skill).limit(20).all()
    skills_list = [s.name for s in skills]
    
    system_message = f"""You are an AI assistant for an ATS (Applicant Tracking System).
    The database contains {candidates_count} candidates and {jobs_count} jobs.
    Available skills in the system: {', '.join(skills_list)}
    
    When the user asks about candidates, provide specific advice on what filters to use.
    Your response should be helpful and actionable."""
    
    prompt = f"""User query: {query}

Based on the ATS database, provide a helpful response. If the user is looking for specific candidates,
suggest what criteria to search for."""
    
    try:
        response = await call_openrouter_api(prompt, system_message)
        
        # Extract candidate/job IDs if mentioned (simple heuristic)
        candidate_ids = []
        job_ids = []
        
        # Try to find relevant candidates based on query keywords
        query_lower = query.lower()
        
        # Simple keyword matching for demo
        if any(word in query_lower for word in ["python", "developer", "engineer"]):
            candidates = db.query(models.Candidate).limit(5).all()
            candidate_ids = [str(c.id) for c in candidates]
        
        return {
            "response": response,
            "suggested_candidates": candidate_ids,
            "suggested_jobs": job_ids
        }
        
    except Exception as e:
        return {
            "response": f"Error processing query: {str(e)}",
            "suggested_candidates": [],
            "suggested_jobs": []
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

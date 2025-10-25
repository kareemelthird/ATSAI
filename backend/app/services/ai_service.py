import httpx
from typing import Dict, Any, List
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import models
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


async def analyze_resume(text: str, candidate_id: str, db: Session, current_user = None) -> Dict[str, Any]:
    """
    Analyze resume text using AI to extract structured information
    """
    # Get user's personal API key if configured
    user_api_key = None
    if current_user and hasattr(current_user, 'use_personal_ai_key') and current_user.use_personal_ai_key:
        user_api_key = getattr(current_user, 'personal_groq_api_key', None)
    
    system_message = """You are an expert HR assistant that analyzes resumes. 
Extract the following information from the resume text and return it as JSON:

IMPORTANT: 
- Extract full name, email, phone from the resume
- For skills, each skill MUST have a "name" field with the actual skill name.

Example format:
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "+1234567890",
  "location": "City, Country",
  "linkedin": "linkedin.com/in/johndoe",
  "github": "github.com/johndoe",
  "portfolio": "johndoe.com",
  "summary": "Professional summary of the candidate",
  "skills": [
    {"name": "Python", "category": "technical"},
    {"name": "JavaScript", "category": "technical"},
    {"name": "Communication", "category": "soft"}
  ],
  "work_experience": [
    {"company": "Company Name", "title": "Job Title", "description": "What they did", "is_current": false}
  ],
  "education": [
    {"institution": "University", "degree": "Bachelor", "field": "Computer Science"}
  ]
}

Return ONLY valid JSON, no additional text."""
    
    prompt = f"""Analyze this resume and extract structured information:

{text}

Return the analysis as JSON."""
    
    try:
        response = await call_ai_api(prompt, system_message, user_api_key)
        
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
            
            # Create candidate
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
                work_exp = models.WorkExperience(
                    candidate_id=candidate_id,
                    company_name=exp.get("company", "Unknown"),
                    job_title=exp.get("title", "Unknown"),
                    responsibilities=exp.get("description", ""),
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
    
    # Create AI prompt with better instructions
    system_message = """You are a professional HR AI assistant helping recruiters find the best candidates.

IMPORTANT INSTRUCTIONS:
- Give direct, natural, conversational answers based ONLY on the candidate data provided
- ALWAYS use the exact names and information from the candidate profiles below
- Be friendly and helpful
- When comparing candidates, provide specific details about BOTH candidates' experience and skills
- Support both English and Arabic queries
- Keep answers concise but informative
- Don't be overly formal or robotic
- If asked about strengths/weaknesses, analyze the candidate's profile and give honest insights based on their CV
- When asked "should I hire X?", provide a balanced assessment based on their qualifications
- NEVER say you don't have information if the candidate data is provided below
- MAINTAIN CONVERSATION CONTEXT: If the user asks follow-up questions like "why?", "tell me more", or "what about him?", refer to the previous conversation to understand what they're asking about
- When user asks "لماذا؟" (why?) or similar, explain your previous recommendation with specific details from the candidate's profile

Example good responses:
- "Ahmed has strong SharePoint and Power Platform development skills with X years of experience..."
- "بناءً على سيرته الذاتية، أحمد لديه خبرة قوية في..."
- "Comparing Adham and Ahmed: Adham specializes in..., while Ahmed focuses on..."
"""

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

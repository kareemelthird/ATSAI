"""
Enhanced AI Service for Intelligent Resume Parsing and Analysis
Extracts maximum information from CVs to populate the enhanced database schema
"""

import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import models
import re


class EnhancedAIService:
    """AI service optimized for comprehensive CV data extraction"""
    
    def __init__(self):
        self.api_url = self._get_api_url()
        self.api_key = self._get_api_key()
        self.model = settings.AI_MODEL
        
    def _get_api_url(self) -> str:
        """Get the appropriate API URL based on provider"""
        provider_urls = {
            "groq": settings.GROQ_API_URL,
            "deepseek": settings.DEEPSEEK_API_URL,
            "openrouter": settings.OPENROUTER_API_URL
        }
        return provider_urls.get(settings.AI_PROVIDER, settings.GROQ_API_URL)
    
    def _get_api_key(self) -> str:
        """Get the appropriate API key based on provider"""
        provider_keys = {
            "groq": settings.GROQ_API_KEY,
            "deepseek": settings.DEEPSEEK_API_KEY,
            "openrouter": settings.OPENROUTER_API_KEY
        }
        return provider_keys.get(settings.AI_PROVIDER, settings.GROQ_API_KEY)
    
    async def call_ai(self, prompt: str, system_message: str) -> str:
        """Call AI API with error handling"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for factual extraction
            "max_tokens": 4000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ AI API Error: {str(e)}")
            raise
    
    async def analyze_resume_comprehensive(self, resume_text: str) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of resume - extracts ALL useful information
        Returns structured data ready for database insertion
        """
        
        system_message = """You are an expert HR AI assistant that extracts detailed information from resumes.
Your job is to analyze the resume text and extract MAXIMUM information in a structured JSON format.

Extract ALL available information including:
1. Basic info (name, email, phone, location, LinkedIn, GitHub, portfolio)
2. Professional summary and career level assessment
3. ALL work experiences with full details (company, role, dates, achievements, technologies, team context)
4. ALL education entries (degree, institution, grades, achievements)
5. ALL skills with proficiency estimation and categorization
6. Projects with technologies and highlights
7. Certifications with dates and issuers
8. Languages spoken with proficiency
9. Career insights (strengths, expertise areas, industry experience)
10. Availability and salary expectations if mentioned
11. Location preferences and relocation willingness

Be thorough and extract every useful detail. Estimate proficiency levels based on context.
Format dates as YYYY-MM-DD. Return valid JSON only."""

        prompt = f"""Analyze this resume and extract ALL information in the following JSON structure:

{{
  "basic_info": {{
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone": "",
    "current_location": "",
    "linkedin_url": "",
    "github_url": "",
    "portfolio_url": "",
    "personal_website": ""
  }},
  "professional": {{
    "professional_summary": "AI-generated 2-3 sentence summary",
    "career_level": "Entry|Mid|Senior|Lead|Manager|Director|Executive",
    "total_years_experience": 0,
    "availability_status": "Immediately|2 weeks|1 month|etc",
    "open_to_relocation": false,
    "willing_to_travel": false,
    "preferred_locations": []
  }},
  "work_experience": [
    {{
      "company_name": "",
      "company_industry": "Fintech|Healthcare|E-commerce|etc",
      "company_size": "Startup|SME|Enterprise",
      "job_title": "",
      "job_level": "Junior|Mid|Senior|Lead|Manager",
      "employment_type": "Full-time|Part-time|Contract|Freelance",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD or null if current",
      "is_current": false,
      "responsibilities": "Detailed description",
      "achievements": ["Achievement 1", "Achievement 2"],
      "technologies_used": ["Python", "React", "AWS"],
      "methodologies": ["Agile", "Scrum"],
      "team_size": 0,
      "managed_team_size": 0,
      "key_metrics": {{"metric_name": "value"}}
    }}
  ],
  "education": [
    {{
      "institution": "",
      "degree": "Bachelor|Master|PhD|Diploma",
      "field_of_study": "",
      "specialization": "",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "graduation_year": 2020,
      "grade_type": "GPA|Percentage|Class",
      "grade_value": "3.8|85%|First Class",
      "achievements": ["Dean's List"],
      "relevant_coursework": ["Course 1"]
    }}
  ],
  "skills": [
    {{
      "skill_name": "Python",
      "skill_category": "Technical|Soft|Language|Tool|Methodology",
      "skill_type": "Programming|Framework|Database|Cloud|etc",
      "proficiency_level": "Beginner|Intermediate|Advanced|Expert",
      "years_of_experience": 0.0,
      "acquired_from": "Self-taught|Course|Work|Education"
    }}
  ],
  "projects": [
    {{
      "project_name": "",
      "project_type": "Personal|Professional|Open Source|Freelance",
      "description": "",
      "role": "Developer|Lead|Contributor",
      "technologies_used": ["Tech1", "Tech2"],
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "project_url": "",
      "github_url": "",
      "highlights": ["Highlight 1"]
    }}
  ],
  "certifications": [
    {{
      "certification_name": "",
      "issuing_organization": "",
      "issue_date": "YYYY-MM-DD",
      "expiry_date": "YYYY-MM-DD or null",
      "credential_id": "",
      "skill_validated": "AWS|Python|etc"
    }}
  ],
  "languages": [
    {{
      "language_name": "English",
      "proficiency_level": "Native|Fluent|Professional|Limited",
      "can_read": true,
      "can_write": true,
      "can_speak": true,
      "certification": "TOEFL|IELTS|etc"
    }}
  ],
  "ai_insights": {{
    "career_trajectory": "AI describes career progression pattern",
    "strengths": ["Strength 1", "Strength 2"],
    "areas_of_expertise": ["Domain 1", "Domain 2"],
    "industry_experience": ["Industry 1", "Industry 2"],
    "one_line_summary": "One sentence about this candidate",
    "elevator_pitch": "2-3 sentences selling this candidate",
    "extracted_keywords": ["keyword1", "keyword2"],
    "overall_experience_score": 85,
    "technical_depth_score": 90,
    "leadership_score": 70,
    "communication_score": 80
  }},
  "smart_tags": [
    {{
      "tag_name": "Cloud Expert",
      "tag_category": "expertise|experience_type|soft_skill|industry",
      "confidence": 0.95
    }}
  ]
}}

RESUME TEXT:
{resume_text}

Extract ALL information found in the resume. If information is not available, use null or empty values.
Be thorough - extract every skill, every job, every detail mentioned.
Return ONLY valid JSON, no additional text."""

        try:
            response = await self.call_ai(prompt, system_message)
            
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            parsed_data = json.loads(response)
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {str(e)}")
            print(f"Response was: {response[:500]}")
            raise Exception("AI returned invalid JSON")
        except Exception as e:
            print(f"❌ Resume Analysis Error: {str(e)}")
            raise
    
    async def save_candidate_from_analysis(
        self, 
        analysis: Dict[str, Any], 
        resume_file_info: Dict[str, str],
        db: Session
    ) -> models.Candidate:
        """
        Save analyzed resume data to database using enhanced schema
        Creates candidate with all related entities
        """
        
        # Create candidate
        basic = analysis.get("basic_info", {})
        professional = analysis.get("professional", {})
        
        candidate = models.Candidate(
            first_name=basic.get("first_name", "Unknown"),
            last_name=basic.get("last_name", ""),
            email=basic.get("email", f"unknown_{datetime.now().timestamp()}@temp.com"),
            phone=basic.get("phone"),
            current_location=basic.get("current_location"),
            preferred_locations=professional.get("preferred_locations", []),
            open_to_relocation=professional.get("open_to_relocation", False),
            willing_to_travel=professional.get("willing_to_travel", False),
            professional_summary=professional.get("professional_summary"),
            career_level=professional.get("career_level"),
            availability_status=professional.get("availability_status"),
            linkedin_url=basic.get("linkedin_url"),
            github_url=basic.get("github_url"),
            portfolio_url=basic.get("portfolio_url"),
            personal_website=basic.get("personal_website"),
            status="active"
        )
        
        db.add(candidate)
        db.flush()  # Get candidate ID
        
        # Add Skills
        for skill_data in analysis.get("skills", []):
            skill = models.Skill(
                candidate_id=candidate.id,
                skill_name=skill_data.get("skill_name"),
                skill_category=skill_data.get("skill_category"),
                skill_type=skill_data.get("skill_type"),
                proficiency_level=skill_data.get("proficiency_level"),
                years_of_experience=skill_data.get("years_of_experience"),
                acquired_from=skill_data.get("acquired_from")
            )
            db.add(skill)
        
        # Add Work Experience
        for exp_data in analysis.get("work_experience", []):
            work_exp = models.WorkExperience(
                candidate_id=candidate.id,
                company_name=exp_data.get("company_name"),
                company_industry=exp_data.get("company_industry"),
                company_size=exp_data.get("company_size"),
                job_title=exp_data.get("job_title"),
                job_level=exp_data.get("job_level"),
                employment_type=exp_data.get("employment_type"),
                start_date=self._parse_date(exp_data.get("start_date")),
                end_date=self._parse_date(exp_data.get("end_date")),
                is_current=exp_data.get("is_current", False),
                responsibilities=exp_data.get("responsibilities"),
                achievements=exp_data.get("achievements", []),
                technologies_used=exp_data.get("technologies_used", []),
                methodologies=exp_data.get("methodologies", []),
                team_size=exp_data.get("team_size"),
                managed_team_size=exp_data.get("managed_team_size"),
                key_metrics=exp_data.get("key_metrics")
            )
            db.add(work_exp)
        
        # Add Education
        for edu_data in analysis.get("education", []):
            education = models.Education(
                candidate_id=candidate.id,
                institution=edu_data.get("institution"),
                degree=edu_data.get("degree"),
                field_of_study=edu_data.get("field_of_study"),
                specialization=edu_data.get("specialization"),
                start_date=self._parse_date(edu_data.get("start_date")),
                end_date=self._parse_date(edu_data.get("end_date")),
                graduation_year=edu_data.get("graduation_year"),
                grade_type=edu_data.get("grade_type"),
                grade_value=edu_data.get("grade_value"),
                achievements=edu_data.get("achievements", []),
                relevant_coursework=edu_data.get("relevant_coursework", [])
            )
            db.add(education)
        
        # Add Projects
        for proj_data in analysis.get("projects", []):
            project = models.Project(
                candidate_id=candidate.id,
                project_name=proj_data.get("project_name"),
                project_type=proj_data.get("project_type"),
                description=proj_data.get("description"),
                role=proj_data.get("role"),
                technologies_used=proj_data.get("technologies_used", []),
                start_date=self._parse_date(proj_data.get("start_date")),
                end_date=self._parse_date(proj_data.get("end_date")),
                project_url=proj_data.get("project_url"),
                github_url=proj_data.get("github_url"),
                highlights=proj_data.get("highlights", [])
            )
            db.add(project)
        
        # Add Certifications
        for cert_data in analysis.get("certifications", []):
            certification = models.Certification(
                candidate_id=candidate.id,
                certification_name=cert_data.get("certification_name"),
                issuing_organization=cert_data.get("issuing_organization"),
                issue_date=self._parse_date(cert_data.get("issue_date")),
                expiry_date=self._parse_date(cert_data.get("expiry_date")),
                credential_id=cert_data.get("credential_id"),
                skill_validated=cert_data.get("skill_validated")
            )
            db.add(certification)
        
        # Add Languages
        for lang_data in analysis.get("languages", []):
            language = models.Language(
                candidate_id=candidate.id,
                language_name=lang_data.get("language_name"),
                proficiency_level=lang_data.get("proficiency_level"),
                can_read=lang_data.get("can_read", True),
                can_write=lang_data.get("can_write", True),
                can_speak=lang_data.get("can_speak", True),
                certification=lang_data.get("certification")
            )
            db.add(language)
        
        # Add AI Analysis
        insights = analysis.get("ai_insights", {})
        ai_analysis = models.AIAnalysis(
            candidate_id=candidate.id,
            ai_model_used=f"{settings.AI_PROVIDER.title()} {self.model}",
            career_trajectory=insights.get("career_trajectory"),
            strengths=insights.get("strengths", []),
            areas_of_expertise=insights.get("areas_of_expertise", []),
            overall_experience_score=insights.get("overall_experience_score"),
            technical_depth_score=insights.get("technical_depth_score"),
            leadership_score=insights.get("leadership_score"),
            communication_score=insights.get("communication_score"),
            extracted_keywords=insights.get("extracted_keywords", []),
            industry_experience=insights.get("industry_experience", []),
            one_line_summary=insights.get("one_line_summary"),
            elevator_pitch=insights.get("elevator_pitch"),
            extraction_confidence=0.90,
            raw_analysis=analysis
        )
        db.add(ai_analysis)
        
        # Add Smart Tags
        for tag_data in analysis.get("smart_tags", []):
            tag = models.CandidateTag(
                candidate_id=candidate.id,
                tag_name=tag_data.get("tag_name"),
                tag_category=tag_data.get("tag_category"),
                confidence=tag_data.get("confidence", 0.8),
                source="ai_extracted"
            )
            db.add(tag)
        
        # Add Resume Record
        resume = models.Resume(
            candidate_id=candidate.id,
            original_filename=resume_file_info.get("filename"),
            file_path=resume_file_info.get("filepath"),
            file_size_bytes=resume_file_info.get("filesize"),
            mime_type=resume_file_info.get("mimetype"),
            extracted_text=resume_file_info.get("text"),
            parse_status="success",
            version=1
        )
        db.add(resume)
        
        db.commit()
        db.refresh(candidate)
        
        return candidate
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str or date_str == "null":
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None
    
    async def chat_with_database(self, query: str, db: Session) -> Dict[str, Any]:
        """
        Enhanced AI chat that understands the rich database structure
        """
        
        # Get all candidates with full context
        candidates = db.query(models.Candidate).all()
        
        if not candidates:
            return {
                "response": "No candidates found in the database. Please upload some resumes first!",
                "candidates": [],
                "jobs": []
            }
        
        # Build comprehensive context
        context_parts = []
        candidate_ids = []
        
        for candidate in candidates:
            candidate_ids.append(str(candidate.id))
            
            # Get latest AI analysis
            ai_analysis = db.query(models.AIAnalysis).filter(
                models.AIAnalysis.candidate_id == candidate.id
            ).order_by(models.AIAnalysis.analysis_date.desc()).first()
            
            # Build rich candidate profile
            skills = [f"{s.skill_name} ({s.proficiency_level})" for s in candidate.skills]
            
            work_exp = []
            for exp in sorted(candidate.work_experiences, key=lambda x: x.start_date or date.min, reverse=True):
                work_exp.append(
                    f"• {exp.job_title} at {exp.company_name} "
                    f"({exp.company_industry or 'N/A'}) - "
                    f"{len(exp.technologies_used or [])} technologies"
                )
            
            education = [f"{e.degree} in {e.field_of_study} from {e.institution}" 
                        for e in candidate.educations]
            
            certifications = [f"{c.certification_name} ({c.issuing_organization})" 
                            for c in candidate.certifications]
            
            languages = [f"{l.language_name} ({l.proficiency_level})" 
                        for l in candidate.languages]
            
            tags = [t.tag_name for t in candidate.tags]
            
            candidate_info = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CANDIDATE: {candidate.first_name} {candidate.last_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email: {candidate.email}
📍 Location: {candidate.current_location or 'Not specified'}
💼 Career Level: {candidate.career_level or 'Not specified'}
📊 Status: {candidate.availability_status or 'Not specified'}

💡 SUMMARY:
{candidate.professional_summary or 'No summary available'}

{'🎯 AI PITCH: ' + ai_analysis.elevator_pitch if ai_analysis and ai_analysis.elevator_pitch else ''}

🔧 SKILLS ({len(skills)}):
{', '.join(skills[:15]) if skills else 'No skills listed'}

💼 WORK EXPERIENCE ({len(candidate.work_experiences)}):
{chr(10).join(work_exp[:5]) if work_exp else 'No experience listed'}

🎓 EDUCATION:
{', '.join(education) if education else 'No education listed'}

📜 CERTIFICATIONS:
{', '.join(certifications) if certifications else 'No certifications'}

🌐 LANGUAGES:
{', '.join(languages) if languages else 'No languages specified'}

🏷️ TAGS:
{', '.join(tags) if tags else 'No tags'}

{'📈 SCORES: ' + f"Experience: {ai_analysis.overall_experience_score}/100, Technical: {ai_analysis.technical_depth_score}/100, Leadership: {ai_analysis.leadership_score}/100" if ai_analysis else ''}
"""
            context_parts.append(candidate_info)
        
        database_context = "\n".join(context_parts)
        
        # AI System Message
        system_message = """You are an expert AI HR assistant for an Applicant Tracking System.

You have access to a comprehensive database of candidates with detailed information including:
- Professional summaries and career levels
- Complete skill sets with proficiency levels
- Detailed work experience with companies, industries, and technologies
- Educational background
- Certifications and languages
- AI-generated insights and scores
- Smart tags and categorizations

Your job is to:
1. Answer HR questions intelligently based on the candidate database
2. Recommend candidates for specific roles or requirements
3. Compare candidates and highlight strengths/gaps
4. Provide insights about the talent pool
5. Explain your recommendations clearly

Be conversational, professional, and thorough. Reference specific candidates by name.
When recommending candidates, explain WHY they're a good fit based on their complete profile.
Consider career level, skills, experience, industries worked in, and AI scores."""

        user_prompt = f"""HR Question: {query}

CANDIDATE DATABASE:
{database_context}

Please provide a detailed, helpful answer based on the candidate information above."""

        try:
            print(f"🤖 AI Chat Query: {query}")
            ai_response = await self.call_ai(user_prompt, system_message)
            print(f"✅ AI Response generated ({len(ai_response)} chars)")
            
            return {
                "response": ai_response,
                "candidates": candidate_ids,
                "jobs": []
            }
            
        except Exception as e:
            print(f"❌ Chat Error: {str(e)}")
            return {
                "response": f"I encountered an error while analyzing the candidates: {str(e)}",
                "candidates": [],
                "jobs": []
            }

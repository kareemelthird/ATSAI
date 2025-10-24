from sqlalchemy.orm import Session
from app.db import models
from typing import Optional
from uuid import UUID


async def calculate_match_score(
    candidate_id: UUID,
    job_id: UUID,
    db: Session
) -> float:
    """
    Calculate match score between a candidate and a job.
    Returns a score from 0 to 100.
    """
    # Get candidate skills (skill names)
    candidate_skills = db.query(models.Skill).filter(
        models.Skill.candidate_id == candidate_id
    ).all()
    
    # Create set of candidate skill names (case-insensitive)
    candidate_skill_names = {skill.skill_name.lower().strip() for skill in candidate_skills if skill.skill_name}
    
    # Get job
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        return 0.0
    
    # Get job required and preferred skills
    required_skills = job.required_skills if job.required_skills else []
    preferred_skills = job.preferred_skills if job.preferred_skills else []
    
    if not required_skills and not preferred_skills:
        # No skills defined for job, return neutral score
        return 50.0
    
    # Count matching skills (case-insensitive comparison)
    matched_required = sum(
        1 for skill in required_skills 
        if skill.lower().strip() in candidate_skill_names
    )
    
    matched_preferred = sum(
        1 for skill in preferred_skills 
        if skill.lower().strip() in candidate_skill_names
    )
    
    # Calculate score
    # Required skills are worth 70%, preferred skills 30%
    total_required = len(required_skills) if required_skills else 1
    total_preferred = len(preferred_skills) if preferred_skills else 1
    
    required_score = (matched_required / total_required) * 70
    preferred_score = (matched_preferred / total_preferred) * 30
    
    total_score = required_score + preferred_score
    
    return round(total_score, 2)


async def get_top_matches_for_job(
    job_id: UUID,
    db: Session,
    limit: int = 10,
    min_score: float = 50.0
) -> list:
    """
    Get top matching candidates for a job
    """
    # Get all candidates
    candidates = db.query(models.Candidate).filter(
        models.Candidate.status == "active"
    ).all()
    
    matches = []
    for candidate in candidates:
        # Check if already applied
        existing_app = db.query(models.Application).filter(
            models.Application.candidate_id == candidate.id,
            models.Application.job_id == job_id
        ).first()
        
        score = await calculate_match_score(candidate.id, job_id, db)
        
        if score >= min_score:
            matches.append({
                "candidate": candidate,
                "score": score,
                "has_applied": existing_app is not None
            })
    
    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    return matches[:limit]

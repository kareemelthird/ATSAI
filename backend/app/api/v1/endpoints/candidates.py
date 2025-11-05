from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
import os
from datetime import datetime, date
from collections import Counter

from app.db.database import get_db
from app.db import models
from app.schemas.schemas import (
    CandidateCreate, 
    CandidateUpdate, 
    CandidateResponse
)
from app.core.auth import get_current_user
from app.db.models_users import User

router = APIRouter()


def calculate_total_years_of_experience(db: Session, candidate_id: UUID) -> int:
    """Calculate total years of experience from all work experience records"""
    try:
        work_experiences = db.query(models.WorkExperience).filter(
            models.WorkExperience.candidate_id == candidate_id
        ).all()
        
        if not work_experiences:
            return 0
            
        total_months = 0
        for exp in work_experiences:
            if exp.duration_months:
                total_months += exp.duration_months
            elif exp.start_date:
                # Calculate duration if not stored
                end_date = exp.end_date or datetime.utcnow().date()
                if exp.start_date <= end_date:
                    delta = end_date - exp.start_date
                    months = round(delta.days / 30.44)  # Average days per month
                    total_months += months
        
        # Convert months to years, rounded to nearest integer
        total_years = round(total_months / 12)
        return max(0, min(total_years, 50))  # Cap at 50 years for sanity
        
    except Exception as e:
        print(f"⚠️ Error calculating total years of experience: {e}")
        return 0


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    """Create a new candidate"""
    # Check if email already exists
    existing = db.query(models.Candidate).filter(
        models.Candidate.email == candidate.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_candidate = models.Candidate(**candidate.model_dump())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@router.get("/", response_model=List[CandidateResponse])
def list_candidates(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List all candidates with optional filtering (basic info only for performance)"""
    query = db.query(models.Candidate)
    
    if status:
        query = query.filter(models.Candidate.status == status)
    
    candidates = query.offset(skip).limit(limit).all()
    
    # Return basic candidate info without loading all relationships (for performance)
    results = []
    for candidate in candidates:
        result = {
            **{k: v for k, v in candidate.__dict__.items() if not k.startswith('_')},
            'id': candidate.id,
            'skills': [],
            'work_experiences': [],
            'educations': [],
            'projects': [],
            'certifications': [],
            'languages': []
        }
        results.append(result)
    
    return results


@router.get("/{candidate_id}")
def get_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific candidate by ID with all related data"""
    from sqlalchemy.orm import selectinload
    from decimal import Decimal
    import traceback
    import sys
    
    try:
        candidate = db.query(models.Candidate).options(
            selectinload(models.Candidate.skills),
            selectinload(models.Candidate.work_experiences),
            selectinload(models.Candidate.educations),
            selectinload(models.Candidate.projects),
            selectinload(models.Candidate.certifications),
            selectinload(models.Candidate.languages)
        ).filter(
            models.Candidate.id == candidate_id
        ).first()
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR loading candidate: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading candidate: {str(e)}"
        )
    
    # Helper to safely convert Decimal to float
    def safe_decimal(value):
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        return value
    
    # Build response manually to ensure proper serialization
    try:
        result = {
        'id': str(candidate.id),
        'first_name': candidate.first_name,
        'last_name': candidate.last_name,
        'email': candidate.email,
        'phone': candidate.phone,
        'current_location': candidate.current_location,
        'summary': candidate.professional_summary,  # Map to summary for backward compatibility
        'linkedin_url': candidate.linkedin_url,
        'github_url': candidate.github_url,
        'portfolio_url': candidate.portfolio_url,
        'status': candidate.status,
        'created_at': candidate.created_at.isoformat() if candidate.created_at else None,
        'updated_at': candidate.updated_at.isoformat() if candidate.updated_at else None,
        'preferred_locations': candidate.preferred_locations or [],
        'open_to_relocation': candidate.open_to_relocation,
        'willing_to_travel': candidate.willing_to_travel,
        'professional_summary': candidate.professional_summary,
        'career_level': candidate.career_level,
        'years_of_experience': candidate.years_of_experience,
        'availability_status': candidate.availability_status,
        'notice_period_days': candidate.notice_period_days,
        'current_salary_currency': candidate.current_salary_currency,
        'current_salary_amount': safe_decimal(candidate.current_salary_amount),
        'expected_salary_currency': candidate.expected_salary_currency,
        'expected_salary_amount': safe_decimal(candidate.expected_salary_amount),
        'personal_website': candidate.personal_website,
        'last_active_at': candidate.last_active_at.isoformat() if candidate.last_active_at else None,
        'skills': [
            {
                'id': str(skill.id),
                'skill_name': skill.skill_name,
                'skill_category': skill.skill_category,
                'skill_type': skill.skill_type,
                'proficiency_level': skill.proficiency_level,
                'years_of_experience': safe_decimal(skill.years_of_experience),
                'last_used_date': skill.last_used_date.isoformat() if skill.last_used_date else None,
                'certification_name': skill.certification_name
            } for skill in candidate.skills
        ] if candidate.skills else [],
        'work_experiences': [
            {
                'id': str(exp.id),
                'job_title': exp.job_title,
                'company_name': exp.company_name,
                'company_location': exp.company_location,
                'company_industry': exp.company_industry,
                'employment_type': exp.employment_type,
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'is_current_job': exp.is_current,  # Fixed: is_current not is_current_job
                'job_description': exp.responsibilities,  # Fixed: responsibilities not job_description
                'key_achievements': ', '.join(exp.achievements) if exp.achievements else None,  # Fixed: achievements is array
                'technologies_used': exp.technologies_used
            } for exp in candidate.work_experiences
        ] if candidate.work_experiences else [],
        'educations': [
            {
                'id': str(edu.id),
                'institution_name': edu.institution,  # Fixed: institution not institution_name
                'institution_location': None,  # Not in model
                'degree_type': edu.degree,  # Fixed: degree not degree_type
                'field_of_study': edu.field_of_study,
                'start_date': edu.start_date.isoformat() if edu.start_date else None,
                'end_date': edu.end_date.isoformat() if edu.end_date else None,
                'gpa': edu.grade_value,  # Fixed: grade_value not gpa
                'gpa_scale': edu.grade_type,  # Fixed: grade_type not gpa_scale
                'achievements': ', '.join(edu.achievements) if edu.achievements else None,  # Fixed: achievements is array
                'is_highest_degree': None  # Not in model
            } for edu in candidate.educations
        ] if candidate.educations else [],
        'projects': [
            {
                'id': str(proj.id),
                'project_name': proj.project_name,
                'role': proj.role,
                'description': proj.description,
                'start_date': proj.start_date.isoformat() if proj.start_date else None,
                'end_date': proj.end_date.isoformat() if proj.end_date else None,
                'technologies_used': proj.technologies_used,
                'project_url': proj.project_url,
                'github_url': proj.github_url
            } for proj in candidate.projects
        ] if candidate.projects else [],
        'certifications': [
            {
                'id': str(cert.id),
                'certification_name': cert.certification_name,
                'issuing_organization': cert.issuing_organization,
                'issue_date': cert.issue_date.isoformat() if cert.issue_date else None,
                'expiry_date': cert.expiry_date.isoformat() if cert.expiry_date else None,
                'credential_id': cert.credential_id,
                'credential_url': cert.credential_url
            } for cert in candidate.certifications
        ] if candidate.certifications else [],
        'languages': [
            {
                'id': str(lang.id),
                'language_name': lang.language_name,
                'proficiency_level': lang.proficiency_level,
                'is_native': lang.proficiency_level == 'Native' if lang.proficiency_level else False  # Fixed: derived from proficiency_level
            } for lang in candidate.languages
        ] if candidate.languages else []
        }
        
        return result
    except Exception as e:
        print(f"ERROR building candidate response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building candidate response: {str(e)}"
        )


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: UUID,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a candidate with complete data including related entities"""
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    try:
        # Update basic candidate fields
        update_data = candidate_update.model_dump(exclude_unset=True, exclude={
            'skills', 'work_experiences', 'education', 'projects', 'certifications', 'languages'
        })
        
        # Handle field mappings for compatibility
        if 'availability' in update_data:
            update_data['availability_status'] = update_data.pop('availability')
        
        if 'expected_salary_min' in update_data:
            update_data['expected_salary_amount'] = update_data.pop('expected_salary_min')
            
        if 'salary_currency' in update_data:
            update_data['expected_salary_currency'] = update_data.pop('salary_currency')
        
        # Update candidate fields
        for field, value in update_data.items():
            if hasattr(candidate, field):
                setattr(candidate, field, value)
        
        # Update related data if provided
        update_data_full = candidate_update.model_dump(exclude_unset=True)
        
        # Update Skills
        if 'skills' in update_data_full and update_data_full['skills'] is not None:
            # Delete existing skills
            db.query(models.Skill).filter(models.Skill.candidate_id == candidate_id).delete()
            
            # Add new skills
            for skill_data in update_data_full['skills']:
                skill = models.Skill(
                    candidate_id=candidate_id,
                    skill_name=skill_data.get('skill_name', ''),
                    proficiency_level=skill_data.get('proficiency_level', 'Intermediate'),
                    years_of_experience=skill_data.get('years_of_experience', 0),
                    skill_category=skill_data.get('category', 'Technical')
                )
                db.add(skill)
        
        # Update Work Experiences
        if 'work_experiences' in update_data_full and update_data_full['work_experiences'] is not None:
            # Delete existing work experiences
            db.query(models.WorkExperience).filter(models.WorkExperience.candidate_id == candidate_id).delete()
            
            # Add new work experiences
            for exp_data in update_data_full['work_experiences']:
                # Parse dates safely - handle empty strings and None values
                start_date = None
                if exp_data.get('start_date') and exp_data['start_date'].strip():
                    try:
                        start_date = datetime.strptime(exp_data['start_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                end_date = None
                if exp_data.get('end_date') and exp_data['end_date'].strip():
                    try:
                        end_date = datetime.strptime(exp_data['end_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                exp = models.WorkExperience(
                    candidate_id=candidate_id,
                    company_name=exp_data.get('company_name', ''),
                    job_title=exp_data.get('position', ''),  # Map 'position' to 'job_title'
                    start_date=start_date,
                    end_date=end_date,
                    responsibilities=exp_data.get('responsibilities'),
                    achievements=exp_data.get('achievements'),
                    employment_type=exp_data.get('employment_type', 'Full-time')
                )
                db.add(exp)
        
        # Update Education
        if 'education' in update_data_full and update_data_full['education'] is not None:
            # Delete existing education
            db.query(models.Education).filter(models.Education.candidate_id == candidate_id).delete()
            
            # Add new education
            for edu_data in update_data_full['education']:
                # Parse dates safely - handle empty strings and None values
                start_date = None
                if edu_data.get('start_date') and edu_data['start_date'].strip():
                    try:
                        start_date = datetime.strptime(edu_data['start_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                end_date = None
                if edu_data.get('end_date') and edu_data['end_date'].strip():
                    try:
                        end_date = datetime.strptime(edu_data['end_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                edu = models.Education(
                    candidate_id=candidate_id,
                    institution=edu_data.get('institution_name', ''),  # Map 'institution_name' to 'institution'
                    degree=edu_data.get('degree', ''),
                    field_of_study=edu_data.get('field_of_study'),
                    start_date=start_date,
                    end_date=end_date,
                    grade_value=edu_data.get('grade')  # Map 'grade' to 'grade_value'
                )
                db.add(edu)
        
        # Update Projects
        if 'projects' in update_data_full and update_data_full['projects'] is not None:
            # Delete existing projects
            db.query(models.Project).filter(models.Project.candidate_id == candidate_id).delete()
            
            # Add new projects
            for proj_data in update_data_full['projects']:
                # Parse dates safely - handle empty strings and None values
                start_date = None
                if proj_data.get('start_date') and proj_data['start_date'].strip():
                    try:
                        start_date = datetime.strptime(proj_data['start_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                end_date = None
                if proj_data.get('end_date') and proj_data['end_date'].strip():
                    try:
                        end_date = datetime.strptime(proj_data['end_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                proj = models.Project(
                    candidate_id=candidate_id,
                    project_name=proj_data.get('project_name', ''),
                    description=proj_data.get('description'),
                    technologies_used=proj_data.get('technologies_used', []),
                    role=proj_data.get('role'),
                    start_date=start_date,
                    end_date=end_date,
                    project_url=proj_data.get('project_url')
                )
                db.add(proj)
        
        # Update Certifications
        if 'certifications' in update_data_full and update_data_full['certifications'] is not None:
            # Delete existing certifications
            db.query(models.Certification).filter(models.Certification.candidate_id == candidate_id).delete()
            
            # Add new certifications
            for cert_data in update_data_full['certifications']:
                # Parse dates safely - handle empty strings and None values
                issue_date = None
                if cert_data.get('issue_date') and cert_data['issue_date'].strip():
                    try:
                        issue_date = datetime.strptime(cert_data['issue_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                expiry_date = None
                if cert_data.get('expiry_date') and cert_data['expiry_date'].strip():
                    try:
                        expiry_date = datetime.strptime(cert_data['expiry_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as None if parsing fails
                
                cert = models.Certification(
                    candidate_id=candidate_id,
                    certification_name=cert_data.get('certification_name', ''),
                    issuing_organization=cert_data.get('issuing_organization', ''),
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    credential_id=cert_data.get('credential_id'),
                    credential_url=cert_data.get('credential_url')
                )
                db.add(cert)
        
        # Update Languages
        if 'languages' in update_data_full and update_data_full['languages'] is not None:
            # Delete existing languages
            db.query(models.Language).filter(models.Language.candidate_id == candidate_id).delete()
            
            # Add new languages
            for lang_data in update_data_full['languages']:
                lang = models.Language(
                    candidate_id=candidate_id,
                    language_name=lang_data.get('language_name', ''),
                    proficiency_level=lang_data.get('proficiency_level', 'Intermediate')
                )
                db.add(lang)
        
        # Update the updated_at timestamp
        candidate.updated_at = datetime.utcnow()
        
        # Recalculate total years of experience from work experience records
        total_years = calculate_total_years_of_experience(db, candidate_id)
        candidate.years_of_experience = total_years
        
        db.commit()
        db.refresh(candidate)
        
        # Return the updated candidate with all related data
        return get_candidate(candidate_id, db)
        
    except Exception as e:
        db.rollback()
        print(f"Error updating candidate: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error updating candidate: {str(e)}"
        )


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a candidate"""
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    db.delete(candidate)
    db.commit()
    return None


@router.get("/{candidate_id}/complete")
def get_candidate_complete(
    candidate_id: UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get complete candidate details with all related data and statistics"""
    
    # Get candidate
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Get all related data
    skills = db.query(models.Skill).filter(
        models.Skill.candidate_id == candidate_id
    ).all()
    
    work_experiences = db.query(models.WorkExperience).filter(
        models.WorkExperience.candidate_id == candidate_id
    ).order_by(models.WorkExperience.start_date.desc()).all()
    
    educations = db.query(models.Education).filter(
        models.Education.candidate_id == candidate_id
    ).order_by(models.Education.end_date.desc()).all()
    
    projects = db.query(models.Project).filter(
        models.Project.candidate_id == candidate_id
    ).order_by(models.Project.start_date.desc()).all()
    
    certifications = db.query(models.Certification).filter(
        models.Certification.candidate_id == candidate_id
    ).order_by(models.Certification.issue_date.desc()).all()
    
    languages = db.query(models.Language).filter(
        models.Language.candidate_id == candidate_id
    ).all()
    
    applications = db.query(models.Application).filter(
        models.Application.candidate_id == candidate_id
    ).order_by(models.Application.applied_date.desc()).all()
    
    # Calculate statistics
    stats = {}
    
    # Total years of experience
    total_months = sum([
        exp.duration_months or 0 
        for exp in work_experiences
    ])
    stats['total_years_experience'] = round(total_months / 12, 1) if total_months else 0
    
    # Skills breakdown by category
    skills_by_category = {}
    for skill in skills:
        category = skill.skill_category or 'Other'
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append({
            'name': skill.skill_name,
            'proficiency': skill.proficiency_level,
            'years': float(skill.years_of_experience) if skill.years_of_experience else 0
        })
    stats['skills_by_category'] = skills_by_category
    
    # Skills by proficiency level
    proficiency_counts = Counter([
        skill.proficiency_level for skill in skills if skill.proficiency_level
    ])
    stats['skills_by_proficiency'] = dict(proficiency_counts)
    
    # Top skills by experience
    top_skills = sorted(
        [s for s in skills if s.years_of_experience],
        key=lambda x: float(x.years_of_experience),
        reverse=True
    )[:10]
    stats['top_skills'] = [
        {
            'name': s.skill_name,
            'years': float(s.years_of_experience),
            'proficiency': s.proficiency_level
        }
        for s in top_skills
    ]
    
    # Work experience summary
    companies = [exp.company_name for exp in work_experiences]
    stats['total_companies'] = len(companies)
    stats['current_company'] = work_experiences[0].company_name if work_experiences and work_experiences[0].is_current else None
    
    # Industry experience
    industries = Counter([
        exp.company_industry for exp in work_experiences if exp.company_industry
    ])
    stats['industries'] = dict(industries)
    
    # Education level
    degrees = [edu.degree for edu in educations if edu.degree]  # Filter out null degrees
    stats['highest_degree'] = degrees[0] if degrees else None
    stats['total_degrees'] = len(degrees)
    
    # Certifications count
    active_certs = [cert for cert in certifications if cert.is_active]
    stats['total_certifications'] = len(certifications)
    stats['active_certifications'] = len(active_certs)
    
    # Projects count
    stats['total_projects'] = len(projects)
    project_types = Counter([
        proj.project_type for proj in projects if proj.project_type
    ])
    stats['projects_by_type'] = dict(project_types)
    
    # Languages spoken
    stats['languages_spoken'] = len(languages)
    
    # Application stats
    stats['total_applications'] = len(applications)
    application_statuses = Counter([
        app.status for app in applications
    ])
    stats['applications_by_status'] = dict(application_statuses)
    
    # Technologies used across all experiences and projects
    all_technologies = []
    for exp in work_experiences:
        if exp.technologies_used:
            all_technologies.extend(exp.technologies_used)
    for proj in projects:
        if proj.technologies_used:
            all_technologies.extend(proj.technologies_used)
    
    tech_counter = Counter(all_technologies)
    stats['top_technologies'] = [
        {'name': tech, 'count': count}
        for tech, count in tech_counter.most_common(15)
    ]
    
    # Career progression (job levels over time)
    career_progression = []
    for exp in reversed(work_experiences):
        if exp.job_level and exp.start_date:
            career_progression.append({
                'level': exp.job_level,
                'title': exp.job_title,
                'company': exp.company_name,
                'date': exp.start_date.isoformat()
            })
    stats['career_progression'] = career_progression
    
    # Prepare response
    return {
        'candidate': {
            'id': str(candidate.id),
            'first_name': candidate.first_name,
            'last_name': candidate.last_name,
            'email': candidate.email,
            'phone': candidate.phone,
            'current_location': candidate.current_location,
            'preferred_locations': candidate.preferred_locations,
            'open_to_relocation': candidate.open_to_relocation,
            'willing_to_travel': candidate.willing_to_travel,
            'professional_summary': candidate.professional_summary,
            'career_level': candidate.career_level,
            'availability_status': candidate.availability_status,
            'notice_period_days': candidate.notice_period_days,
            'current_salary_currency': candidate.current_salary_currency,
            'current_salary_amount': float(candidate.current_salary_amount) if candidate.current_salary_amount else None,
            'expected_salary_currency': candidate.expected_salary_currency,
            'expected_salary_amount': float(candidate.expected_salary_amount) if candidate.expected_salary_amount else None,
            'linkedin_url': candidate.linkedin_url,
            'github_url': candidate.github_url,
            'portfolio_url': candidate.portfolio_url,
            'personal_website': candidate.personal_website,
            'created_at': candidate.created_at.isoformat() if candidate.created_at else None,
            'updated_at': candidate.updated_at.isoformat() if candidate.updated_at else None,
            'status': candidate.status
        },
        'skills': [
            {
                'id': str(s.id),
                'skill_name': s.skill_name,
                'skill_category': s.skill_category,
                'skill_type': s.skill_type,
                'proficiency_level': s.proficiency_level,
                'years_of_experience': float(s.years_of_experience) if s.years_of_experience else None,
                'last_used_date': s.last_used_date.isoformat() if s.last_used_date else None,
            }
            for s in skills
        ],
        'work_experiences': [
            {
                'id': str(exp.id),
                'company_name': exp.company_name,
                'company_industry': exp.company_industry,
                'company_size': exp.company_size,
                'job_title': exp.job_title,
                'job_level': exp.job_level,
                'employment_type': exp.employment_type,
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'is_current': exp.is_current,
                'duration_months': exp.duration_months,
                'responsibilities': exp.responsibilities,
                'achievements': exp.achievements,
                'technologies_used': exp.technologies_used,
                'team_size': exp.team_size,
                'managed_team_size': exp.managed_team_size,
            }
            for exp in work_experiences
        ],
        'educations': [
            {
                'id': str(edu.id),
                'institution': edu.institution,
                'degree': edu.degree,
                'field_of_study': edu.field_of_study,
                'specialization': edu.specialization,
                'start_date': edu.start_date.isoformat() if edu.start_date else None,
                'end_date': edu.end_date.isoformat() if edu.end_date else None,
                'graduation_year': edu.graduation_year,
                'grade_type': edu.grade_type,
                'grade_value': edu.grade_value,
                'achievements': edu.achievements,
            }
            for edu in educations
        ],
        'projects': [
            {
                'id': str(proj.id),
                'project_name': proj.project_name,
                'project_type': proj.project_type,
                'description': proj.description,
                'role': proj.role,
                'technologies_used': proj.technologies_used,
                'start_date': proj.start_date.isoformat() if proj.start_date else None,
                'end_date': proj.end_date.isoformat() if proj.end_date else None,
                'project_url': proj.project_url,
                'github_url': proj.github_url,
                'highlights': proj.highlights,
            }
            for proj in projects
        ],
        'certifications': [
            {
                'id': str(cert.id),
                'certification_name': cert.certification_name,
                'issuing_organization': cert.issuing_organization,
                'issue_date': cert.issue_date.isoformat() if cert.issue_date else None,
                'expiry_date': cert.expiry_date.isoformat() if cert.expiry_date else None,
                'is_active': cert.is_active,
                'credential_url': cert.credential_url,
            }
            for cert in certifications
        ],
        'languages': [
            {
                'id': str(lang.id),
                'language_name': lang.language_name,
                'proficiency_level': lang.proficiency_level,
            }
            for lang in languages
        ],
        'applications': [
            {
                'id': str(app.id),
                'job_id': str(app.job_id),
                'status': app.status,
                'applied_at': app.applied_date.isoformat() if app.applied_date else None,
            }
            for app in applications
        ],
        'statistics': stats
    }


@router.get("/{candidate_id}/resume/download")
def download_candidate_resume(
    candidate_id: UUID,
    db: Session = Depends(get_db)
):
    """Download the most recent resume for a candidate"""
    try:
        # Get the most recent resume with a valid file path for this candidate
        resume = db.query(models.Resume).filter(
            models.Resume.candidate_id == candidate_id,
            models.Resume.file_path.isnot(None),
            models.Resume.file_path != ''
        ).order_by(models.Resume.upload_date.desc()).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found for this candidate"
            )
        
        # Handle different file path formats
        file_path = resume.file_path
        possible_paths = []
        
        # Try different path combinations based on environment
        if not os.path.isabs(file_path):
            from pathlib import Path
            
            # Local development paths
            workspace_root = Path(__file__).parent.parent.parent.parent.parent.parent
            workspace_path = workspace_root / file_path
            cwd_path = Path.cwd() / file_path
            
            # Production/Vercel paths (ephemeral storage)
            vercel_tmp_path = Path("/tmp/uploads") / os.path.basename(file_path)
            vercel_tmp_path2 = Path("/tmp") / os.path.basename(file_path)
            
            possible_paths = [
                str(workspace_path),  # Local development
                str(cwd_path),        # Current working directory
                str(vercel_tmp_path), # Vercel tmp uploads
                str(vercel_tmp_path2),# Vercel tmp root
                file_path             # Original path
            ]
        else:
            possible_paths = [file_path]
        
        # Find the first existing file
        existing_file = None
        for path in possible_paths:
            normalized_path = os.path.normpath(path)
            if os.path.exists(normalized_path):
                existing_file = normalized_path
                break
        
        # If file doesn't exist anywhere, check if we have extracted text
        if not existing_file:
            if resume.extracted_text:
                # Create a temporary text file with the CV content
                import tempfile
                import io
                
                # Create in-memory text content
                cv_content = f"""
RESUME: {resume.original_filename}
Uploaded: {resume.upload_date}
Candidate ID: {candidate_id}

EXTRACTED CONTENT:
{resume.extracted_text}
                """.strip()
                
                # Return as downloadable text file
                from fastapi.responses import Response
                
                return Response(
                    content=cv_content.encode('utf-8'),
                    media_type="text/plain",
                    headers={
                        "Content-Disposition": f"attachment; filename=\"{resume.original_filename}.txt\""
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resume file not found and no extracted text available. Original file: {resume.original_filename}"
                )
        
        # Return the found file
        return FileResponse(
            path=existing_file,
            media_type="application/pdf",
            filename=resume.original_filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading resume: {str(e)}"
        )


@router.delete("/{candidate_id}/resume", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate_resume(
    candidate_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete all resumes for a candidate"""
    # Get all resumes for this candidate
    resumes = db.query(models.Resume).filter(
        models.Resume.candidate_id == candidate_id
    ).all()
    
    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resumes found for this candidate"
        )
    
    # Delete physical files
    for resume in resumes:
        if resume.file_path and os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
            except Exception as e:
                print(f"Warning: Could not delete file {resume.file_path}: {e}")
    
    # Delete database records
    db.query(models.Resume).filter(
        models.Resume.candidate_id == candidate_id
    ).delete()
    db.commit()
    
    return None


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db import models
from app.schemas.schemas import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse
)
from app.services.matching_service import calculate_match_score

router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create a new job application"""
    
    # Validate candidate exists
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == application.candidate_id
    ).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Validate job exists
    job = db.query(models.Job).filter(
        models.Job.id == application.job_id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check for duplicate application
    existing = db.query(models.Application).filter(
        models.Application.candidate_id == application.candidate_id,
        models.Application.job_id == application.job_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application already exists"
        )
    
    # Create application
    db_application = models.Application(**application.model_dump())
    
    # Calculate match score
    match_score = await calculate_match_score(
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        db=db
    )
    db_application.match_score = match_score
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("/", response_model=List[ApplicationResponse])
def list_applications(
    skip: int = 0,
    limit: int = 100,
    candidate_id: UUID = None,
    job_id: UUID = None,
    db: Session = Depends(get_db)
):
    """List applications with optional filtering"""
    query = db.query(models.Application)
    
    if candidate_id:
        query = query.filter(models.Application.candidate_id == candidate_id)
    
    if job_id:
        query = query.filter(models.Application.job_id == job_id)
    
    applications = query.offset(skip).limit(limit).all()
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific application"""
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update an application"""
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    return application

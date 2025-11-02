from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import os
from pathlib import Path
from datetime import datetime

from app.db.database import get_db
from app.db import models
from app.schemas.schemas import ResumeResponse
from app.services.pdf_parser import parse_pdf
from app.services.ai_service import analyze_resume
from app.core.config import settings
from app.core.auth import get_current_user
from app.db.models_users import User

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume_auto(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a resume and automatically create/update candidate with AI-extracted data"""
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file temporarily with unique name
    temp_filename = f"temp_{datetime.utcnow().timestamp()}_{file.filename}"
    temp_file_path = upload_dir / temp_filename
    
    try:
        # Read and save file
        content = await file.read()
        with open(temp_file_path, "wb") as buffer:
            buffer.write(content)
        
        # Parse PDF to extract text
        extracted_text = parse_pdf(str(temp_file_path))
        
        # Use AI to analyze resume and extract structured data
        # This will create the candidate and all related records automatically
        # Pass current_user to use their personal API key if configured
        try:
            ai_result = await analyze_resume(extracted_text, None, db, current_user)
        except Exception as ai_error:
            print(f"AI analysis failed: {ai_error}")
            # Fallback: Create a basic candidate record without AI analysis
            from datetime import datetime
            import uuid
            
            candidate = models.Candidate(
                first_name="Unknown",
                last_name="Candidate", 
                email=f"candidate_{uuid.uuid4().hex[:8]}@temp.com",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(candidate)
            db.flush()
            
            ai_result = {
                'candidate_id': str(candidate.id),
                'note': 'Created without AI analysis due to processing error'
            }
        
        if not ai_result or not ai_result.get('candidate_id'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract candidate information from resume"
            )
        
        candidate_id = ai_result['candidate_id']
        
        # Rename file to use actual candidate_id
        final_file_path = upload_dir / f"{candidate_id}_{file.filename}"
        
        # Remove existing file if it exists, then rename
        if final_file_path.exists():
            final_file_path.unlink()  # Delete existing file
        
        if temp_file_path.exists():
            temp_file_path.rename(final_file_path)
        
        # Count existing versions for this candidate
        version = db.query(models.Resume).filter(
            models.Resume.candidate_id == candidate_id
        ).count() + 1
        
        # Create resume record
        resume = models.Resume(
            candidate_id=candidate_id,
            original_filename=file.filename,
            file_path=str(final_file_path),
            file_size_bytes=len(content),
            mime_type=file.content_type or "application/pdf",
            version=version,
            extracted_text=extracted_text,
            parse_status="success",
            last_parsed_date=datetime.utcnow()
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return resume
        
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file_path and temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except:
                pass
        
        # Log the detailed error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing resume upload: {str(e)}")
        print(f"Full traceback: {error_details}")
        
        # Return user-friendly error message
        error_msg = str(e)
        if "AI" in error_msg or "analyze" in error_msg.lower():
            error_msg = "AI processing failed. Please try again or contact support if the issue persists."
        elif "file" in error_msg.lower() or "path" in error_msg.lower():
            error_msg = "File processing failed. Please ensure the PDF is not corrupted."
        elif "database" in error_msg.lower():
            error_msg = "Database error occurred. Please try again."
        else:
            error_msg = f"Error processing resume: {str(e)}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.post("/upload/{candidate_id}", response_model=ResumeResponse)
async def upload_resume(
    candidate_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a resume for a candidate"""
    
    # Validate candidate exists
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / f"{candidate_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Count existing versions
    version = db.query(models.Resume).filter(
        models.Resume.candidate_id == candidate_id
    ).count() + 1
    
    # Create resume record
    resume = models.Resume(
        candidate_id=candidate_id,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=len(content),
        mime_type=file.content_type,
        version=version,
        parse_status="pending"
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    # Parse PDF in background (for now, synchronous)
    try:
        extracted_text = parse_pdf(str(file_path))
        resume.extracted_text = extracted_text
        resume.parse_status = "success"
        resume.last_parsed_date = datetime.utcnow()
        
        # Trigger AI analysis with user's personal API key if configured
        ai_result = await analyze_resume(extracted_text, candidate_id, db, current_user)
        
        db.commit()
        db.refresh(resume)
    except Exception as e:
        resume.parse_status = "failed"
        resume.parse_error = str(e)
        db.commit()
    
    return resume


@router.get("/candidate/{candidate_id}", response_model=List[ResumeResponse])
def get_candidate_resumes(
    candidate_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all resumes for a candidate"""
    resumes = db.query(models.Resume).filter(
        models.Resume.candidate_id == candidate_id
    ).order_by(models.Resume.version.desc()).all()
    
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific resume"""
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file from disk
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    db.delete(resume)
    db.commit()
    return None

"""
Simple test endpoint for debugging PDF upload issues
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import os

from app.db.database import get_db
from app.core.config import settings
from app.core.auth import get_current_user
from app.db.models_users import User
from app.services.pdf_parser import parse_pdf

router = APIRouter()

@router.post("/test-upload")
async def test_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simple upload test without AI processing"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in [".pdf"]:
            raise HTTPException(status_code=400, detail="Only PDF files allowed for test")
        
        # Create upload directory
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        temp_filename = f"test_{file.filename}"
        temp_file_path = upload_dir / temp_filename
        
        content = await file.read()
        with open(temp_file_path, "wb") as buffer:
            buffer.write(content)
        
        # Test PDF parsing
        try:
            extracted_text = parse_pdf(str(temp_file_path))
            text_preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        except Exception as pdf_error:
            text_preview = f"PDF parsing failed: {str(pdf_error)}"
        
        # Clean up
        if temp_file_path.exists():
            os.remove(temp_file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_size": len(content),
            "upload_dir": str(upload_dir),
            "text_preview": text_preview,
            "user": current_user.email
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
"""
Simple Upload Test Endpoint - No AI Processing
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import os
from pathlib import Path
import traceback

from app.db.database import get_db
from app.core.config import settings
from app.core.auth import get_current_user
from app.db.models_users import User

router = APIRouter()

@router.post("/simple-upload")
async def simple_upload_test(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Simple upload test without AI processing"""
    
    try:
        print(f"🔍 Simple upload test started")
        print(f"   File: {file.filename}")
        print(f"   Content-Type: {file.content_type}")
        print(f"   User: {current_user.email}")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        print(f"   Extension: {file_ext}")
        
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return {
                "status": "error",
                "message": f"File type {file_ext} not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            }
        
        # Test directory creation
        upload_dir = Path(settings.UPLOAD_DIR)
        print(f"   Upload dir: {upload_dir}")
        
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Directory created/verified")
        except Exception as dir_error:
            print(f"   ❌ Directory error: {dir_error}")
            return {
                "status": "error", 
                "message": f"Directory error: {str(dir_error)}"
            }
        
        # Test file reading
        try:
            content = await file.read()
            file_size = len(content)
            print(f"   ✅ File read successfully: {file_size} bytes")
        except Exception as read_error:
            print(f"   ❌ File read error: {read_error}")
            return {
                "status": "error",
                "message": f"File read error: {str(read_error)}"
            }
        
        # Test file writing
        temp_filename = f"test_{datetime.utcnow().timestamp()}_{file.filename}"
        temp_file_path = upload_dir / temp_filename
        
        try:
            with open(temp_file_path, "wb") as buffer:
                buffer.write(content)
            print(f"   ✅ File written successfully: {temp_file_path}")
        except Exception as write_error:
            print(f"   ❌ File write error: {write_error}")
            return {
                "status": "error",
                "message": f"File write error: {str(write_error)}"
            }
        
        # Test PDF parsing (if it's a PDF)
        pdf_text = None
        if file_ext == '.pdf':
            try:
                from app.services.pdf_parser import parse_pdf
                pdf_text = parse_pdf(str(temp_file_path))
                print(f"   ✅ PDF parsed successfully: {len(pdf_text)} characters")
            except Exception as pdf_error:
                print(f"   ❌ PDF parsing error: {pdf_error}")
                pdf_text = f"PDF parsing failed: {str(pdf_error)}"
        
        # Clean up test file
        try:
            if temp_file_path.exists():
                os.remove(temp_file_path)
                print(f"   ✅ Test file cleaned up")
        except Exception as cleanup_error:
            print(f"   ⚠️ Cleanup error: {cleanup_error}")
        
        return {
            "status": "success",
            "message": "Upload test completed successfully",
            "details": {
                "filename": file.filename,
                "size": file_size,
                "content_type": file.content_type,
                "upload_dir": str(upload_dir),
                "pdf_text_length": len(pdf_text) if pdf_text else None,
                "pdf_preview": pdf_text[:200] if pdf_text else None
            }
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Simple upload test failed: {str(e)}")
        print(f"Full traceback: {error_details}")
        
        return {
            "status": "error",
            "message": f"Upload test failed: {str(e)}",
            "traceback": error_details
        }
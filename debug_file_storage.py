#!/usr/bin/env python3

"""
Debug File Storage Issue
========================

Check where files are being stored and if they exist
"""

import sys
sys.path.append("./backend")

from app.db.database import SessionLocal
from app.db.models import Resume
import os
from pathlib import Path

def debug_file_storage():
    """Debug file storage paths and existence"""
    
    print("🔍 Debugging File Storage Issue")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Get all resumes with file paths
        resumes = db.query(Resume).filter(
            Resume.file_path.isnot(None),
            Resume.file_path != ''
        ).order_by(Resume.upload_date.desc()).limit(10).all()
        
        print(f"📁 Found {len(resumes)} resumes with file paths:")
        
        for resume in resumes:
            print(f"\\n📄 Resume: {resume.original_filename}")
            print(f"   Candidate ID: {resume.candidate_id}")
            print(f"   Stored path: {resume.file_path}")
            print(f"   Upload date: {resume.upload_date}")
            
            # Check if file exists
            file_path = resume.file_path
            
            # Try different path combinations
            paths_to_check = [
                file_path,  # Original path
                os.path.abspath(file_path),  # Absolute path
                Path.cwd() / file_path,  # Current working directory
                Path(__file__).parent / file_path,  # Script directory
                f"/tmp/{os.path.basename(file_path)}",  # Vercel temp path
            ]
            
            file_found = False
            for path in paths_to_check:
                if os.path.exists(str(path)):
                    print(f"   ✅ File found at: {path}")
                    print(f"   📏 File size: {os.path.getsize(str(path))} bytes")
                    file_found = True
                    break
            
            if not file_found:
                print(f"   ❌ File not found in any of these locations:")
                for path in paths_to_check:
                    print(f"      - {path}")
        
        # Check current working directory and uploads folder
        print(f"\\n📂 Current working directory: {Path.cwd()}")
        
        uploads_dirs = [
            Path.cwd() / "uploads",
            Path(__file__).parent / "uploads",
            Path("/tmp/uploads"),
            Path("/tmp"),
        ]
        
        for uploads_dir in uploads_dirs:
            if uploads_dir.exists():
                print(f"✅ Uploads directory found: {uploads_dir}")
                files = list(uploads_dir.glob("*"))
                print(f"   Contains {len(files)} files")
                for file in files[:5]:  # Show first 5 files
                    print(f"      - {file.name}")
            else:
                print(f"❌ Directory not found: {uploads_dir}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_file_storage()
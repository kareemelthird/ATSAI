"""Test script to debug the download endpoint"""
from app.db.database import get_db
from app.db import models
from uuid import UUID
from pathlib import Path
import os

# Get database session
db = next(get_db())

# Test candidate ID
candidate_id = UUID('92203af8-cb9b-4b87-9a07-e6b049dcb145')

# Query resume
resume = db.query(models.Resume).filter(
    models.Resume.candidate_id == candidate_id,
    models.Resume.file_path != None,
    models.Resume.file_path != ""
).order_by(models.Resume.version.desc()).first()

print(f"Resume found: {resume is not None}")
if resume:
    print(f"File path in DB: {resume.file_path}")
    print(f"Original filename: {resume.original_filename}")
    
    # Test path construction
    file_path = resume.file_path
    print(f"\nInitial file_path: {file_path}")
    print(f"Is absolute: {os.path.isabs(file_path)}")
    
    if not os.path.isabs(file_path):
        backend_dir = Path(__file__).parent
        print(f"Backend dir: {backend_dir}")
        file_path = str(backend_dir / file_path)
        print(f"Combined path: {file_path}")
    
    file_path = os.path.normpath(file_path)
    print(f"Normalized path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        print(f"File size: {os.path.getsize(file_path)} bytes")

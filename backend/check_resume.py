from app.db.database import get_db
from app.db import models
from uuid import UUID
import os

db = next(get_db())
candidate_id = UUID('92203af8-cb9b-4b87-9a07-e6b049dcb145')

resume = db.query(models.Resume).filter(
    models.Resume.candidate_id == candidate_id
).order_by(models.Resume.version.desc()).first()

print(f'Resume found: {resume is not None}')
if resume:
    print(f'File path: {resume.file_path}')
    print(f'Original filename: {resume.original_filename}')
    print(f'File exists: {os.path.exists(resume.file_path) if resume.file_path else False}')
else:
    print('No resume found for this candidate!')

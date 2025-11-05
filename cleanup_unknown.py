"""
Clean up Unknown candidates
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.db import models

def cleanup_unknown_candidates():
    """Remove candidates with Unknown names and temp emails"""
    
    print("🧹 Cleaning up Unknown Candidates")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        # Find candidates with "Unknown" names and temp emails
        unknown_candidates = db.query(models.Candidate).filter(
            models.Candidate.first_name == "Unknown",
            models.Candidate.email.like("temp_%@temp.com")
        ).all()
        
        print(f"Found {len(unknown_candidates)} Unknown candidates to clean up:")
        
        for candidate in unknown_candidates:
            print(f"  Deleting: {candidate.first_name} {candidate.last_name} - {candidate.email}")
            
            # Delete related data first
            db.query(models.Skill).filter(models.Skill.candidate_id == candidate.id).delete()
            db.query(models.WorkExperience).filter(models.WorkExperience.candidate_id == candidate.id).delete()
            db.query(models.Education).filter(models.Education.candidate_id == candidate.id).delete()
            db.query(models.Project).filter(models.Project.candidate_id == candidate.id).delete()
            db.query(models.Certification).filter(models.Certification.candidate_id == candidate.id).delete()
            
            # Delete the candidate
            db.delete(candidate)
        
        db.commit()
        print(f"✅ Cleaned up {len(unknown_candidates)} candidates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_unknown_candidates()
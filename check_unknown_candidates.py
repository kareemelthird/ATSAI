"""
Check for existing candidates with Unknown names
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.db import models

def check_unknown_candidates():
    """Check for candidates with Unknown names"""
    
    print("🔍 Checking for Unknown Candidates")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        # Find candidates with "Unknown" names
        unknown_candidates = db.query(models.Candidate).filter(
            models.Candidate.first_name == "Unknown"
        ).all()
        
        print(f"Found {len(unknown_candidates)} candidates with 'Unknown' first name:")
        
        for candidate in unknown_candidates:
            print(f"  ID: {candidate.id}")
            print(f"  Name: {candidate.first_name} {candidate.last_name}")
            print(f"  Email: {candidate.email}")
            print(f"  Created: {candidate.created_at}")
            print(f"  Updated: {candidate.updated_at}")
            print("  ---")
        
        # Find candidates with temp emails
        temp_candidates = db.query(models.Candidate).filter(
            models.Candidate.email.like("temp_%@temp.com")
        ).all()
        
        print(f"\\nFound {len(temp_candidates)} candidates with temp emails:")
        
        for candidate in temp_candidates:
            print(f"  ID: {candidate.id}")
            print(f"  Name: {candidate.first_name} {candidate.last_name}")
            print(f"  Email: {candidate.email}")
            print(f"  Summary: {candidate.professional_summary[:100] if candidate.professional_summary else 'None'}...")
            print("  ---")
        
        # Show recent candidates
        recent_candidates = db.query(models.Candidate).order_by(
            models.Candidate.created_at.desc()
        ).limit(5).all()
        
        print(f"\\nRecent 5 candidates:")
        for candidate in recent_candidates:
            print(f"  {candidate.first_name} {candidate.last_name} - {candidate.email}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_unknown_candidates()
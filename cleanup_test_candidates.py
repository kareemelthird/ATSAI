#!/usr/bin/env python3

# Clean up test candidates
import sys
sys.path.append("./backend")

from app.db.database import SessionLocal
from app.db.models import Candidate

def cleanup_test_candidates():
    print("🧹 Cleaning up test candidates")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        # Find test candidates
        test_emails = [
            "john.smith@email.com",
            "ahmed.mohamed@company.com",
            "test@example.com"
        ]
        
        test_candidates = db.query(Candidate).filter(
            Candidate.email.in_(test_emails)
        ).all()
        
        print(f"Found {len(test_candidates)} test candidates:")
        for candidate in test_candidates:
            print(f"  - {candidate.first_name} {candidate.last_name} ({candidate.email})")
        
        if test_candidates:
            # Delete them
            for candidate in test_candidates:
                db.delete(candidate)
            
            db.commit()
            print(f"✅ Cleaned up {len(test_candidates)} test candidates")
        else:
            print("✅ No test candidates to clean up")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_test_candidates()
#!/usr/bin/env python3
"""Test script to verify years of experience calculation"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import Candidate, WorkExperience
from app.api.v1.endpoints.candidates import calculate_total_years_of_experience
from datetime import datetime, date
from uuid import uuid4

def test_years_calculation():
    """Test the years of experience calculation"""
    db = SessionLocal()
    
    try:
        # Find an existing candidate or create one for testing
        candidate = db.query(Candidate).first()
        
        if not candidate:
            print("ℹ️ No existing candidates found. Creating test candidate...")
            # Create a test candidate
            candidate = Candidate(
                id=uuid4(),
                name="Test Candidate",
                email="test@example.com",
                years_of_experience=0
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
            print(f"✅ Created test candidate: {candidate.name} (ID: {candidate.id})")
        else:
            print(f"ℹ️ Using existing candidate: {candidate.name} (ID: {candidate.id})")
        
        # Check existing work experience
        work_experiences = db.query(WorkExperience).filter(
            WorkExperience.candidate_id == candidate.id
        ).all()
        
        print(f"ℹ️ Found {len(work_experiences)} work experience records:")
        total_stored_months = 0
        for i, exp in enumerate(work_experiences, 1):
            print(f"  {i}. {exp.company_name or 'Unknown Company'}: {exp.duration_months or 0} months")
            if exp.duration_months:
                total_stored_months += exp.duration_months
        
        # Calculate total years using our function
        calculated_years = calculate_total_years_of_experience(db, candidate.id)
        stored_years = candidate.years_of_experience or 0
        
        print(f"\n📊 Experience Analysis:")
        print(f"  • Total stored months: {total_stored_months}")
        print(f"  • Expected years: {round(total_stored_months / 12)}")
        print(f"  • Current stored years: {stored_years}")
        print(f"  • Calculated years: {calculated_years}")
        
        # Test the calculation result
        if calculated_years > 0 and len(work_experiences) > 0:
            print(f"✅ Years calculation working! Total: {calculated_years} years")
            
            # Update the candidate's years
            candidate.years_of_experience = calculated_years
            candidate.updated_at = datetime.utcnow()
            db.commit()
            print(f"✅ Updated candidate years of experience to {calculated_years}")
            
        elif len(work_experiences) == 0:
            print("⚠️ No work experience records found - years calculation would be 0")
        else:
            print("❌ Years calculation returned 0 despite having work experience records")
            
        # Double-check the updated value
        db.refresh(candidate)
        print(f"🔍 Final verification: years_of_experience = {candidate.years_of_experience}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_years_calculation()
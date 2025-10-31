#!/usr/bin/env python3
"""
Debug script to test the candidate update API and see the 422 validation errors
"""
import sys
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from app.schemas.schemas import CandidateUpdate
from pydantic import ValidationError

# Sample data that might be coming from the frontend
frontend_data = {
    "first_name": "Abd Elrahman Bahaa Eldin Elsayed",
    "last_name": "Ali",
    "email": "a.rahman_semary@yahoo.com",
    "phone": "+201287807621",
    "current_location": "Some location",
    "professional_summary": "Professional summary",
    "career_level": "Senior",
    "years_of_experience": 5,
    "linkedin_url": "",
    "github_url": "",
    "portfolio_url": "",
    "preferred_locations": [],
    "open_to_relocation": False,
    "willing_to_travel": False,
    "expected_salary_min": 0,
    "expected_salary_max": 0,
    "salary_currency": "USD",
    "availability": "",
    "notice_period_days": 0,
    "skills": [],
    "work_experiences": [],
    "education": [],
    "projects": [],
    "certifications": [],
    "languages": []
}

print("Testing CandidateUpdate validation...")
print("=" * 50)

try:
    # Try to validate the data
    validated_data = CandidateUpdate(**frontend_data)
    print("✅ Validation PASSED!")
    print("Validated data:")
    print(json.dumps(validated_data.model_dump(), indent=2, default=str))
    
except ValidationError as e:
    print("❌ Validation FAILED!")
    print("Validation errors:")
    for error in e.errors():
        field = error.get('loc', ['unknown'])
        message = error.get('msg', 'Unknown error')
        print(f"  - Field: {'.'.join(str(f) for f in field)}")
        print(f"    Error: {message}")
        print(f"    Input: {error.get('input', 'N/A')}")
        print()
        
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
print("Testing with missing fields...")

# Test with minimal data
minimal_data = {
    "first_name": "Test",
    "last_name": "User"
}

try:
    validated_minimal = CandidateUpdate(**minimal_data)
    print("✅ Minimal validation PASSED!")
except ValidationError as e:
    print("❌ Minimal validation FAILED!")
    for error in e.errors():
        field = error.get('loc', ['unknown'])
        message = error.get('msg', 'Unknown error')
        print(f"  - Field: {'.'.join(str(f) for f in field)}: {message}")
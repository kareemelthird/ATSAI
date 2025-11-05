#!/usr/bin/env python3
"""
Test AI chat with job integration - verify mock AI includes real job data
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_service import chat_with_database
from app.db.database import SessionLocal
from app.db import models
from app.core.config import settings

async def test_ai_chat_with_jobs():
    """Test that AI chat includes real job data from database"""
    
    print("🧪 Testing AI Chat with Job Integration")
    print("=" * 50)
    
    # Create a test database session
    db = SessionLocal()
    
    try:
        # First, let's add a test job if none exist
        existing_jobs = db.query(models.Job).filter(models.Job.status == 'open').all()
        
        if not existing_jobs:
            print("📝 Creating test job...")
            test_job = models.Job(
                title="Senior Python Developer",
                department="Engineering",
                location="Cairo, Egypt",
                employment_type="Full-time",
                status="open",
                description="Looking for an experienced Python developer with FastAPI experience",
                required_skills=["Python", "FastAPI", "PostgreSQL", "React"],
                min_experience_years=3,
                max_experience_years=7,
                salary_min=80000,
                salary_max=120000,
                salary_currency="USD"
            )
            db.add(test_job)
            db.commit()
            print("✅ Test job created")
        else:
            print(f"📊 Found {len(existing_jobs)} existing jobs")
            
        # Test chat queries that should include job data
        test_queries = [
            "What jobs are available?",
            "Show me the open positions",
            "ما هي الوظائف المتاحة؟",
            "Tell me about current job openings"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            print("-" * 30)
            
            # Call the chat function
            response = await chat_with_database(query, db, current_user=None)
            
            # Check if response includes job information
            response_text = response.get("response", "")
            jobs_mentioned = response.get("jobs", [])
            
            print(f"📱 Response: {response_text[:200]}...")
            print(f"🎯 Jobs mentioned: {len(jobs_mentioned)}")
            
            # Verify that job information is included
            job_keywords = ["job", "position", "opening", "developer", "وظيفة", "منصب"]
            has_job_content = any(keyword.lower() in response_text.lower() for keyword in job_keywords)
            
            if has_job_content:
                print("✅ Response includes job-related content")
            else:
                print("❌ Response missing job-related content")
                
            print()
        
        print("🎉 AI Chat Job Integration Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_ai_chat_with_jobs())
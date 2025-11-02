#!/usr/bin/env python3
"""
Database initialization script for Vercel deployment
Run this after deploying to Vercel to set up your database tables
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(current_dir))

def setup_database():
    """Initialize database tables and default data"""
    try:
        print("🔄 Initializing database for Vercel deployment...")
        
        # Import after path setup
        from app.db.database import engine
        from app.db import models
        from app.core.config import settings
        
        print(f"📍 Connecting to database: {settings.DATABASE_URL[:50]}...")
        
        # Create all tables
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Run the admin and settings setup
        print("🔄 Setting up default admin user and AI settings...")
        
        # Import setup scripts
        import subprocess
        import sys
        
        # Run admin creation
        result = subprocess.run([sys.executable, "backend/create_admin.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Admin user setup completed")
        else:
            print(f"⚠️  Admin setup output: {result.stdout}")
            print(f"⚠️  Admin setup errors: {result.stderr}")
        
        # Run AI settings creation
        result = subprocess.run([sys.executable, "backend/add_ai_settings.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AI settings setup completed")
        else:
            print(f"⚠️  AI settings output: {result.stdout}")
            print(f"⚠️  AI settings errors: {result.stderr}")
            
        print("\n🎉 Database initialization completed!")
        print("📝 Your ATS application is ready to use.")
        print("🔗 You can now access your deployed application.")
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        print("💡 Make sure:")
        print("   1. DATABASE_URL is correctly set")
        print("   2. Database is accessible from your network")
        print("   3. Required Python packages are installed")
        return False
    
    return True

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable is not set")
        print("💡 Set your production database URL and try again")
        sys.exit(1)
    
    success = setup_database()
    sys.exit(0 if success else 1)
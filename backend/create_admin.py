"""
Create super admin user
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.db.database import SessionLocal
from app.db.models_users import User, UserRole, UserStatus
import bcrypt
import uuid
from datetime import datetime

def create_admin():
    """Create initial super admin user"""
    print("🚀 Creating Super Admin User")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@ats.com").first()
        
        if admin:
            print("⚠️  Super admin already exists!")
            print(f"   📧 Email: {admin.email}")
            print(f"   👤 Username: {admin.username}")
            print(f"   🔐 Role: {admin.role.value}")
            return
        
        # Hash the password using bcrypt directly
        password = "Admin@123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create super admin
        admin = User(
            id=uuid.uuid4(),
            email="admin@ats.com",
            username="admin",
            hashed_password=hashed_password,
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            login_count=0,
            failed_login_attempts=0,
            mfa_enabled=False,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Super admin created successfully!")
        print("=" * 60)
        print("📋 Login Credentials:")
        print("   📧 Email: admin@ats.com")
        print("   🔐 Password: Admin@123")
        print("=" * 60)
        print("⚠️  IMPORTANT: Change this password after first login!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

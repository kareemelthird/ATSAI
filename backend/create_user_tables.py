"""
Create user management tables and seed initial data
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.database import engine, SessionLocal
from app.db.models_users import Base, User, UserRole, UserStatus, SystemSettings
from app.core.auth import hash_password
import uuid
from datetime import datetime

def create_tables():
    """Create all user management tables"""
    print("🔨 Creating user management tables...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ User management tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def seed_admin_user():
    """Create initial super admin user"""
    print("\n👤 Creating super admin user...")
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@ats.com").first()
        
        if admin:
            print("⚠️  Super admin already exists")
            print(f"   Email: {admin.email}")
            return
        
        # Create super admin
        admin = User(
            id=uuid.uuid4(),
            email="admin@ats.com",
            username="admin",
            hashed_password=hash_password("Admin@123"),
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Super admin created successfully!")
        print("   📧 Email: admin@ats.com")
        print("   🔐 Password: Admin@123")
        print("   ⚠️  Please change this password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

def seed_default_settings():
    """Create default system settings"""
    print("\n⚙️  Creating default system settings...")
    
    db = SessionLocal()
    try:
        # Check if settings exist
        if db.query(SystemSettings).count() > 0:
            print("⚠️  Settings already exist")
            return
        
        default_settings = [
            # AI Provider Settings
            SystemSettings(
                category="ai_provider",
                key="active_provider",
                value="openrouter",
                label="Active AI Provider",
                description="Currently active AI provider (openrouter, groq, deepseek)"
            ),
            SystemSettings(
                category="ai_provider",
                key="openrouter_api_key",
                value="",
                label="OpenRouter API Key",
                description="API key for OpenRouter service",
                is_encrypted=True
            ),
            SystemSettings(
                category="ai_provider",
                key="groq_api_key",
                value="",
                label="Groq API Key",
                description="API key for Groq service",
                is_encrypted=True
            ),
            SystemSettings(
                category="ai_provider",
                key="deepseek_api_key",
                value="",
                label="DeepSeek API Key",
                description="API key for DeepSeek service",
                is_encrypted=True
            ),
            
            # Database Settings
            SystemSettings(
                category="database",
                key="connection_pool_size",
                value="10",
                label="Connection Pool Size",
                description="Maximum number of database connections in the pool"
            ),
            SystemSettings(
                category="database",
                key="backup_enabled",
                value="true",
                label="Auto Backup Enabled",
                description="Enable automatic database backups"
            ),
            
            # Email Settings
            SystemSettings(
                category="email",
                key="smtp_host",
                value="",
                label="SMTP Host",
                description="SMTP server hostname"
            ),
            SystemSettings(
                category="email",
                key="smtp_port",
                value="587",
                label="SMTP Port",
                description="SMTP server port"
            ),
            SystemSettings(
                category="email",
                key="smtp_username",
                value="",
                label="SMTP Username",
                description="SMTP authentication username"
            ),
            SystemSettings(
                category="email",
                key="smtp_password",
                value="",
                label="SMTP Password",
                description="SMTP authentication password",
                is_encrypted=True
            ),
            
            # Application Settings
            SystemSettings(
                category="application",
                key="app_name",
                value="ATS System",
                label="Application Name",
                description="Name of the application",
                is_public=True
            ),
            SystemSettings(
                category="application",
                key="session_timeout",
                value="30",
                label="Session Timeout (minutes)",
                description="User session timeout in minutes"
            ),
            SystemSettings(
                category="application",
                key="max_upload_size",
                value="10",
                label="Max Upload Size (MB)",
                description="Maximum file upload size in megabytes"
            ),
            
            # Security Settings
            SystemSettings(
                category="security",
                key="password_min_length",
                value="8",
                label="Minimum Password Length",
                description="Minimum required password length"
            ),
            SystemSettings(
                category="security",
                key="require_special_char",
                value="true",
                label="Require Special Character",
                description="Require at least one special character in passwords"
            ),
            SystemSettings(
                category="security",
                key="max_login_attempts",
                value="5",
                label="Max Login Attempts",
                description="Maximum failed login attempts before account lockout"
            ),
            SystemSettings(
                category="security",
                key="lockout_duration",
                value="30",
                label="Lockout Duration (minutes)",
                description="Account lockout duration in minutes"
            ),
        ]
        
        db.add_all(default_settings)
        db.commit()
        
        print(f"✅ Created {len(default_settings)} default settings")
        
    except Exception as e:
        print(f"❌ Error creating settings: {e}")
        db.rollback()
    finally:
        db.close()

def verify_installation():
    """Verify that tables were created successfully"""
    print("\n🔍 Verifying installation...")
    
    db = SessionLocal()
    try:
        # Check tables exist
        user_count = db.query(User).count()
        settings_count = db.query(SystemSettings).count()
        
        print(f"✅ Users table: {user_count} records")
        print(f"✅ Settings table: {settings_count} records")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        db.close()

def main():
    print("=" * 60)
    print("🚀 ATS User Management System Installation")
    print("=" * 60)
    
    # Step 1: Create tables
    if not create_tables():
        print("\n❌ Installation failed!")
        return
    
    # Step 2: Seed admin user
    seed_admin_user()
    
    # Step 3: Seed default settings
    seed_default_settings()
    
    # Step 4: Verify
    if verify_installation():
        print("\n" + "=" * 60)
        print("✅ Installation completed successfully!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Login with: admin@ats.com / Admin@123")
        print("2. Change the admin password")
        print("3. Configure AI provider settings")
        print("4. Create additional users")
        print("\n🚀 Start the backend server and test the login endpoint!")
        print("=" * 60)
    else:
        print("\n⚠️  Installation completed with warnings")

if __name__ == "__main__":
    main()

"""
Update Admin User Role to Super Admin
"""
import os
import sys
sys.path.append('./backend')

# Set the correct database URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:Nevertry%4012@db.qfyzthlnhhexvulvzonz.supabase.co:5432/postgres'

from app.db.database import get_db
from app.db.models_users import User
from sqlalchemy.orm import Session

def update_admin_role():
    """Update admin user role to super_admin"""
    print("🔧 Updating Admin User Role...")
    print("=" * 40)
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Find the admin user
        admin_user = db.query(User).filter(User.email == 'admin@ats.com').first()
        
        if admin_user:
            print(f"✅ Found user: {admin_user.email}")
            print(f"   Current role: {admin_user.role}")
            print(f"   Current status: {admin_user.status}")
            print(f"   ID: {admin_user.id}")
            
            # Update to super_admin
            old_role = admin_user.role
            admin_user.role = 'super_admin'
            db.commit()
            
            print(f"\n🎯 Role updated:")
            print(f"   From: {old_role}")
            print(f"   To: {admin_user.role}")
            print("\n✅ User role updated successfully!")
            
        else:
            print("❌ Admin user not found")
            
            # List all users to debug
            print("\n🔍 Available users:")
            all_users = db.query(User).all()
            for user in all_users:
                print(f"   - {user.email} (role: {user.role}, status: {user.status})")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_role()
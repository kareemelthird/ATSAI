# 🚀 Quick Start Guide - User Management System

## ✅ What's Already Done

1. **Database tables created** ✅
   - users, user_sessions, audit_logs, system_settings, permissions, notifications

2. **Super admin created** ✅
   - Email: admin@ats.com
   - Password: Admin@123

3. **Authentication system ready** ✅
   - Password hashing (bcrypt)
   - JWT tokens (access + refresh)
   - Role-based authorization

4. **System settings seeded** ✅
   - 17 default settings for AI, database, email, security

## 🎯 What You Need to Do Next

### Option 1: Quick Test (Recommended First)
Let me create a simple login endpoint right now so you can test the system immediately!

### Option 2: Full Implementation
Follow the detailed guides:
- `USER_MANAGEMENT_SETUP.md` - Complete endpoint implementation guide
- `USER_MANAGEMENT_COMPLETE.md` - Full system documentation

## 📝 Quick Commands

### Start Backend
```powershell
cd C:\Users\karim.hassan\ATS
.venv\Scripts\activate
cd backend
python -m uvicorn app.main:app --reload
```

### Test Login (after endpoint created)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ats.com", "password": "Admin@123"}'
```

### Create Another Admin (after endpoint created)
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@ats.com",
    "username": "manager",
    "password": "Manager@123",
    "first_name": "HR",
    "last_name": "Manager",
    "role": "HR_MANAGER"
  }'
```

## 🔑 User Roles Quick Reference

| Role | Access Level | Can Do |
|------|-------------|---------|
| **SUPER_ADMIN** | Full system | Everything |
| **ADMIN** | High | Manage users, settings, all data |
| **HR_MANAGER** | Medium | Manage candidates, jobs, applications |
| **RECRUITER** | Limited | View/manage assigned candidates |
| **VIEWER** | Read-only | View data only |

## 📂 Files You Have

### Core Files (Already Created)
- `/backend/app/db/models_users.py` - User models
- `/backend/app/core/auth.py` - Authentication utilities
- `/backend/app/core/config.py` - Configuration with JWT settings
- `/backend/create_user_tables.py` - Database migration
- `/backend/create_admin.py` - Admin user creation

### Files You Need to Create
1. `/backend/app/api/v1/endpoints/auth.py` - Login, register, logout
2. `/backend/app/api/v1/endpoints/users.py` - User CRUD operations
3. `/backend/app/api/v1/endpoints/settings.py` - Settings management
4. `/frontend/src/pages/Login.tsx` - Login page
5. `/frontend/src/pages/admin/Users.tsx` - User management UI

## 💡 Pro Tips

1. **Test incrementally** - Create login endpoint first, test it, then move to user management
2. **Use the auth utilities** - Import from `app.core.auth` for password hashing and JWT
3. **Check existing code** - Look at `candidates.py` for FastAPI patterns
4. **Use the models** - Import from `app.db.models_users` for User, UserRole, etc.

## 🆘 Need Help?

Ask me to:
- "Create the login endpoint"
- "Create the user management endpoints"
- "Create the settings endpoints"
- "Create the login page"
- "Help me test the authentication"
- "Show me how to protect existing endpoints"

## 📞 Quick Reference - Auth Functions

```python
# In your endpoints, use these:
from app.core.auth import (
    hash_password,           # Hash passwords
    verify_password,         # Verify password
    create_access_token,     # Create JWT token
    create_refresh_token,    # Create refresh token
    get_current_user,        # FastAPI dependency
    check_permission,        # Check user permissions
    log_audit                # Log user actions
)

# Example usage:
@router.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": token}
    raise HTTPException(401, "Invalid credentials")
```

## 🎯 Your Current Status

✅ Database ready  
✅ Admin user created  
✅ Authentication system ready  
✅ Default settings configured  
⏳ Endpoints need to be created  
⏳ Frontend needs to be built  

**You're 60% done with the user management system!**

Would you like me to create the login endpoint for you so you can test it right away? 🚀

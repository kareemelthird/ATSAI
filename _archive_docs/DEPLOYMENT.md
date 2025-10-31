# Deployment Guide - ATS Application

## 🚀 Deploy to Render.com (Recommended - FREE)

Render.com provides free hosting for:
- ✅ PostgreSQL Database (500MB)
- ✅ Backend API (FastAPI)
- ✅ Frontend (React Static Site)

### Prerequisites

1. **GitHub Account** - Your code must be on GitHub
2. **Render Account** - Sign up at https://render.com (free)
3. **Groq API Key** - Get from https://console.groq.com

### Step-by-Step Deployment

#### 1. Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Ready for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ats-application.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Render

**Option A: Using Blueprint (Automatic - Recommended)**

1. Go to https://render.com/dashboard
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create all services
5. Set environment variables:
   - `GROQ_API_KEY` - Your Groq API key
   - `SECRET_KEY` - Will be auto-generated
6. Click **"Apply"**
7. Wait 5-10 minutes for deployment

**Option B: Manual Setup**

1. **Create PostgreSQL Database:**
   - New → PostgreSQL
   - Name: `ats-database`
   - Database: `atsdb`
   - User: `atsuser`
   - Region: Frankfurt (or nearest)
   - Plan: Free

2. **Create Backend Service:**
   - New → Web Service
   - Connect GitHub repo
   - Name: `ats-backend`
   - Root Directory: Leave blank
   - Environment: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free
   - Environment Variables:
     ```
     DATABASE_URL = [Copy from PostgreSQL service]
     SECRET_KEY = [Generate random string]
     GROQ_API_KEY = [Your Groq API key]
     PYTHON_VERSION = 3.11.0
     ```

3. **Create Frontend Service:**
   - New → Static Site
   - Connect GitHub repo
   - Name: `ats-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
   - Environment Variables:
     ```
     VITE_API_URL = https://ats-backend.onrender.com
     ```

#### 3. Initialize Database

After backend is deployed, run migrations:

1. Go to your backend service on Render
2. Click **"Shell"** tab
3. Run:
   ```bash
   cd backend
   python create_tables.py
   python create_admin.py
   ```

#### 4. Access Your Application

- **Frontend:** https://ats-frontend.onrender.com
- **Backend API:** https://ats-backend.onrender.com
- **API Docs:** https://ats-backend.onrender.com/docs

**Default Admin Login:**
- Email: `admin@ats.com`
- Password: `admin123` (Change immediately!)

---

## 🆓 Alternative Free Hosting Options

### Option 2: Railway.app

**Pros:** Faster than Render, good free tier
**Steps:**
1. Sign up at https://railway.app
2. New Project → Deploy from GitHub
3. Add PostgreSQL plugin
4. Add two services: backend and frontend
5. Set environment variables

### Option 3: Vercel (Frontend) + Railway (Backend)

**Pros:** Vercel has excellent frontend performance
**Steps:**
1. Deploy frontend to Vercel: https://vercel.com
2. Deploy backend to Railway: https://railway.app
3. Update `VITE_API_URL` in Vercel to point to Railway backend

### Option 4: Fly.io

**Pros:** Multiple regions, good performance
**Free Tier:** 3 shared VMs, 3GB storage
**Steps:**
1. Install Fly CLI: https://fly.io/docs/getting-started/
2. Run: `fly launch`
3. Deploy: `fly deploy`

---

## ⚙️ Environment Variables Required

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-here-minimum-32-characters

# AI Service
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://your-frontend.com
```

### Frontend (.env)
```env
VITE_API_URL=https://your-backend.com
```

---

## 🔒 Important Security Steps

After deployment:

1. **Change Default Admin Password**
   - Login with `admin@ats.com` / `admin123`
   - Go to Settings → Change password immediately

2. **Update SECRET_KEY**
   - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Update in Render environment variables

3. **Set Allowed Origins**
   - Update `ALLOWED_ORIGINS` in backend config
   - Should match your frontend URL

4. **Add Your Groq API Key**
   - Get from https://console.groq.com/keys
   - Add to backend environment variables

---

## 📊 Free Tier Limitations

### Render.com Free Tier:
- ✅ 750 hours/month (enough for 1 service 24/7)
- ✅ 500MB PostgreSQL database
- ✅ Sleeps after 15 minutes of inactivity
- ✅ 100GB bandwidth/month
- ⚠️ First request after sleep takes 30-60 seconds

### Tips to Stay Within Free Tier:
1. Backend and frontend count as separate services
2. Use single PostgreSQL database for everything
3. Keep database under 500MB
4. Service sleeps when inactive (acceptable for demo)

---

## 🐛 Troubleshooting

### Backend Won't Start
- Check logs in Render dashboard
- Verify `DATABASE_URL` is set correctly
- Ensure `GROQ_API_KEY` is valid
- Check Python version is 3.11+

### Frontend Can't Connect to Backend
- Verify `VITE_API_URL` matches backend URL
- Check CORS settings in backend
- Ensure backend is running (may be sleeping)

### Database Connection Errors
- Verify `DATABASE_URL` format
- Check database is in same region as backend
- Ensure database isn't paused

### "Service Unavailable" After Deploy
- First deploy takes 5-10 minutes
- Check deployment logs for errors
- Verify all environment variables are set

---

## 📱 Custom Domain (Optional)

### Add Custom Domain to Render:
1. Go to service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `ats.yourdomain.com`)
4. Update DNS records as shown
5. Wait for SSL certificate (automatic)

---

## 🔄 Continuous Deployment

Render automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Render automatically deploys in 2-5 minutes
```

---

## 📈 Monitoring

- **Render Dashboard:** View logs, metrics, deployment status
- **Health Check:** https://ats-backend.onrender.com/api/v1/health
- **API Docs:** https://ats-backend.onrender.com/docs

---

## 💰 Upgrade Options

If you need more resources:

**Render Starter Plan ($7/month):**
- No sleep on inactivity
- 1GB RAM
- Faster builds

**PostgreSQL Starter ($7/month):**
- 1GB database
- Daily backups
- Better performance

---

## 🎉 Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Database deployed
- [ ] Backend deployed with all env vars
- [ ] Frontend deployed with API URL
- [ ] Database initialized (tables created)
- [ ] Admin account created
- [ ] Default password changed
- [ ] Application accessible via URLs
- [ ] AI chat working (Groq API key valid)
- [ ] Resume upload working

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **Your App Logs:** Check Render dashboard for each service

---

**Ready to deploy? Start with Step 1: Push to GitHub!** 🚀

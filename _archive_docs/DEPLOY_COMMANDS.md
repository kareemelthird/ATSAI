# 🚀 Quick Deployment Commands

## For Render.com (Recommended)

### 1. First Time Setup

```bash
# Commit everything
git add .
git commit -m "Ready for deployment"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/ats-app.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

Go to: https://render.com/deploy

Or manually:
1. Dashboard → New → Blueprint
2. Connect your GitHub repo
3. Render detects `render.yaml`
4. Set environment variables:
   - `GROQ_API_KEY` = your_key_here
5. Click "Apply"

### 3. Initialize Database

After backend deploys, go to Shell tab:

```bash
cd backend
python create_tables.py
python create_admin.py
```

### 4. Done! 🎉

Your URLs:
- **Frontend**: https://ats-frontend.onrender.com
- **Backend**: https://ats-backend.onrender.com  
- **API Docs**: https://ats-backend.onrender.com/docs

**Login**: admin@ats.com / admin123

---

## For Railway.app

```bash
# Install Railway CLI
npm install -g railway

# Login and deploy
railway login
railway init
railway up
```

---

## For Fly.io

```bash
# Install Fly CLI
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Deploy
fly launch
fly deploy
```

---

## Environment Variables Needed

**Backend:**
- `DATABASE_URL` - Auto-set by Render
- `SECRET_KEY` - Auto-generated
- `GROQ_API_KEY` - Your API key (**Required**)
- `ALLOWED_ORIGINS` - Your frontend URL

**Frontend:**
- `VITE_API_URL` - Your backend URL

---

## Update After Changes

```bash
git add .
git commit -m "Update feature"
git push

# Render auto-deploys in 2-5 minutes
```

---

## Free Deployment Checklist

- [ ] Code committed to git
- [ ] Pushed to GitHub
- [ ] Render account created (free)
- [ ] Blueprint deployed
- [ ] GROQ_API_KEY added
- [ ] Database initialized
- [ ] Admin account created
- [ ] Default password changed
- [ ] Application accessible

---

## Support

Need help? Check:
- `DEPLOYMENT.md` - Detailed guide
- `DEPLOY_NOW.md` - Quick guide  
- `DEPLOYMENT_READY.md` - Overview

**Total time: 10-15 minutes** ⏱️

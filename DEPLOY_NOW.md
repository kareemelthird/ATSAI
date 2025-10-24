# 🚀 Quick Deployment Guide

## Before You Start

- [ ] Have a Groq API key ready (free from https://console.groq.com)
- [ ] Have a GitHub account
- [ ] Have a Render account (free at https://render.com)

## Step 1: Prepare Your Code

```bash
# Make sure everything is committed
git add .
git commit -m "Ready for deployment"
```

## Step 2: Push to GitHub

```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Render

### Quick Setup (Recommended):

1. Go to https://render.com/dashboard
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Set these environment variables:
   - `GROQ_API_KEY`: your_groq_key_here
   - `SECRET_KEY`: (auto-generated)
6. Click **"Apply"**
7. Wait 5-10 minutes ☕

### After Deployment:

1. Go to your backend service Shell tab
2. Run database setup:
```bash
cd backend
python create_tables.py
python create_admin.py
```

3. Access your app:
   - Frontend: `https://ats-frontend.onrender.com`
   - Backend: `https://ats-backend.onrender.com`
   - Docs: `https://ats-backend.onrender.com/docs`

4. Login:
   - Email: `admin@ats.com`
   - Password: `admin123`
   - **CHANGE PASSWORD IMMEDIATELY!**

## URLs You'll Need

After deployment, you'll get:
- ✅ Frontend URL: `https://YOUR_APP-frontend.onrender.com`
- ✅ Backend URL: `https://YOUR_APP-backend.onrender.com`
- ✅ Database URL: (Internal, auto-connected)

## Common Issues

**"Service Unavailable"**
- Wait 30-60 seconds after first deploy
- Free tier services sleep after 15 min of inactivity

**"Can't connect to backend"**
- Update `VITE_API_URL` in frontend service
- Should be: `https://YOUR_APP-backend.onrender.com`

**"Database error"**
- Make sure you ran `create_tables.py` in Shell
- Check `DATABASE_URL` is set correctly

## 🎉 That's It!

Your ATS is now live and accessible to anyone with the URL!

**Important:** Free tier sleeps after 15 minutes of inactivity. First request after sleep takes 30-60 seconds.

## Want Custom Domain?

1. Buy domain from Namecheap/GoDaddy
2. In Render service → Custom Domain
3. Add domain and update DNS records
4. SSL certificate auto-provided

## Need Help?

See `DEPLOYMENT.md` for detailed instructions.

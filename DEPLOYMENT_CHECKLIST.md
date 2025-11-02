# 🚀 Vercel Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Repository Setup
- [ ] All code committed to GitHub repository
- [ ] Repository is public or Vercel has access to private repo
- [ ] No sensitive data in repository (check .env files are in .gitignore)

### 2. Database Setup
- [ ] Cloud PostgreSQL database created (Supabase/Railway/Neon)
- [ ] Database connection string ready
- [ ] Database accessible from internet (not localhost)

### 3. Environment Variables Ready
Create these in Vercel dashboard after connecting your repo:

```env
# ⚠️ REQUIRED - Application will not work without these
DATABASE_URL=postgresql://username:password@host:port/database_name
SECRET_KEY=your-very-long-secret-key-at-least-32-characters

# 🤖 AI Configuration (required for AI features)
USE_MOCK_AI=false
AI_MODEL=llama-3.3-70b-versatile

# 📁 File Upload Settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain

# ⚙️ Application Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=ATS AI
DEBUG=false
```

### 4. AI Settings (if using AI features)
- [ ] Groq API key ready (sign up at groq.com)
- [ ] Add Groq API key to system settings after deployment

## 🚀 Deployment Steps

### Step 1: Connect to Vercel
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Select the repository and click "Deploy"

### Step 2: Configure Project Settings
1. **Project Name**: Choose a memorable name
2. **Framework Preset**: Should auto-detect as "Other"
3. **Root Directory**: Leave as `.` (root)
4. **Build Command**: Leave default (handled by vercel.json)

### Step 3: Add Environment Variables
1. In Vercel project settings, go to "Environment Variables"
2. Add all variables from the list above
3. Set for "Production", "Preview", and "Development" environments

### Step 4: Deploy
1. Click "Deploy" - Vercel will build and deploy automatically
2. Wait for deployment to complete (usually 2-5 minutes)
3. Your app will be available at `https://your-project-name.vercel.app`

### Step 5: Initialize Database
After successful deployment:

1. **Option A: Use the setup script**
   ```bash
   # Clone your repo locally
   git clone your-repo-url
   cd your-project
   
   # Set your production DATABASE_URL
   export DATABASE_URL="your-production-database-url"
   
   # Run setup script
   python setup_vercel_db.py
   ```

2. **Option B: Manual setup**
   ```bash
   cd backend
   # Set DATABASE_URL to your production database
   python create_tables.py
   python create_admin.py
   python add_ai_settings.py
   ```

### Step 6: Test Your Deployment
1. Visit your Vercel URL
2. Check that the homepage loads
3. Try creating an account
4. Test login functionality
5. Upload a sample resume
6. Test AI chat (if configured)

## 🔧 Troubleshooting Common Issues

### Build Failures
- **Check build logs** in Vercel dashboard → Functions tab
- **Common causes**: Missing dependencies, syntax errors, environment variables

### Database Connection Issues
- Verify DATABASE_URL is correct
- Ensure database allows connections from 0.0.0.0 (all IPs)
- Check database service is running

### 404 Errors
- Frontend build might have failed
- Check that vercel.json routing is correct

### API Errors
- Check environment variables are set correctly
- Verify backend is deploying (check Functions tab)
- Look at function logs for errors

### CORS Issues
- Should be handled automatically
- If issues persist, check your domain in CORS settings

## 📊 Post-Deployment

### Performance Monitoring
- Monitor function execution times in Vercel dashboard
- Check error rates and response times
- Set up alerts for critical issues

### Security
- Change default admin password immediately
- Set up proper CORS origins for production
- Enable proper logging

### Backups
- Set up automated database backups
- Export important data regularly
- Document recovery procedures

## 💰 Cost Considerations

### Vercel Free Tier Limits
- 100GB bandwidth per month
- 6,000 serverless function invocations per month
- 100 deployments per day

### Database Providers Free Tiers
- **Supabase**: 2 projects, 500MB database
- **Railway**: $5 credit (1 month free usage)
- **Neon**: 3 projects, 3GB storage

## 🆘 Getting Help

If you encounter issues:

1. **Check Vercel Logs**: Project → Functions → Click function → View logs
2. **Database Connectivity**: Test connection string locally first
3. **Environment Variables**: Double-check all required vars are set
4. **Build Issues**: Check that build works locally first

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Homepage loads without errors
- ✅ Login/registration works
- ✅ File upload functions
- ✅ Database operations work
- ✅ AI features respond (if configured)

---

**🚀 Your ATS AI application is now live on Vercel!**

Share your URL: `https://your-project-name.vercel.app`
# Vercel Deployment Guide

This guide explains how to deploy your ATS AI application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **PostgreSQL Database**: Set up a cloud PostgreSQL database (recommended: Supabase, Railway, or Neon)

## Environment Variables

### Required Environment Variables in Vercel Dashboard

Navigate to your Vercel project settings → Environment Variables and add:

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Authentication (REQUIRED)
SECRET_KEY=your-very-long-secret-key-at-least-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration (REQUIRED if using AI features)
USE_MOCK_AI=false
AI_MODEL=llama-3.3-70b-versatile

# File Upload Settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain

# Application Settings
APP_NAME=ATS AI
DEBUG=false
```

### Frontend Environment Variables

The frontend will automatically use the same domain for API calls in production.

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository structure looks like this:
```
your-repo/
├── frontend/          # React frontend
├── backend/           # FastAPI backend
├── vercel.json        # Vercel configuration
└── README.md
```

### 2. Connect to Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the configuration

### 3. Configure Environment Variables

1. In your Vercel project dashboard, go to "Settings" → "Environment Variables"
2. Add all the required environment variables listed above
3. Make sure to set them for "Production", "Preview", and "Development" environments

### 4. Database Setup

You'll need a cloud PostgreSQL database. Recommended providers:

#### Option A: Supabase (Free tier available)
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string and add it as `DATABASE_URL` in Vercel

#### Option B: Railway (Free tier available)
1. Go to [railway.app](https://railway.app)
2. Create a new PostgreSQL database
3. Copy the connection string

#### Option C: Neon (Free tier available)
1. Go to [neon.tech](https://neon.tech)
2. Create a new database
3. Copy the connection string

### 5. Initialize Database Tables

After deployment, you need to create the database tables:

1. Clone your repository locally
2. Set up your local environment with the production DATABASE_URL
3. Run the table creation script:
   ```bash
   cd backend
   python create_tables.py
   ```

### 6. Deploy

1. Push your changes to GitHub
2. Vercel will automatically deploy your application
3. Your app will be available at `https://your-project-name.vercel.app`

## Project Structure for Vercel

The `vercel.json` configuration handles:

- **Frontend**: Built as a static site and served from the root
- **Backend**: Deployed as serverless functions under `/api/*`
- **API Routes**: All backend routes are accessible at `https://your-domain.com/api/*`

## Troubleshooting

### Common Issues

1. **Build Errors**: Check the build logs in Vercel dashboard
2. **Database Connection**: Ensure your DATABASE_URL is correct and the database is accessible
3. **Environment Variables**: Make sure all required env vars are set
4. **CORS Issues**: The app is configured to allow all origins

### Checking Logs

1. Go to your Vercel project dashboard
2. Click on "Functions" tab
3. Click on any function to see logs

### Testing Your Deployment

1. Visit `https://your-domain.com` - Should show the frontend
2. Visit `https://your-domain.com/api/docs` - Should show FastAPI documentation
3. Try logging in with a test account

## Production Considerations

1. **Security**: Update CORS settings to only allow your domain
2. **Database**: Use connection pooling for production databases
3. **Monitoring**: Set up monitoring and error tracking
4. **Backups**: Ensure your database has regular backups

## Cost Considerations

- **Vercel**: Free tier includes 100GB bandwidth and 6,000 serverless function invocations
- **Database**: Most providers offer free tiers suitable for development/small production use

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify all environment variables are set correctly
3. Ensure your database is accessible from the internet
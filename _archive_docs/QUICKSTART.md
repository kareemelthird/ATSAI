# Quick Start Guide

## Prerequisites Check
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 15+ installed and running
- [ ] OpenRouter API key (get free at https://openrouter.ai)

## Setup Steps

### 1. Configure OpenRouter API Key
Edit `backend/.env` and replace:
```
OPENROUTER_API_KEY=your_actual_key_here
```

### 2. Setup PostgreSQL Database
```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ats_db;
\q
```

### 3. Start Backend
```powershell
cd backend
# Python environment is already configured
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### 4. Start Frontend (in a new terminal)
```powershell
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Testing the Application

### 1. Upload a Resume
1. Go to http://localhost:3000
2. Click "Upload Resume"
3. Fill in candidate information
4. Upload a PDF resume
5. Wait for AI analysis to complete

### 2. View Candidates
- Navigate to "Candidates" page
- Click on a candidate to see details
- View extracted skills, experience, and education

### 3. Try AI Chat
- Go to "AI Chat" page
- Ask: "Find me Python developers"
- See AI-powered responses

### 4. Create Jobs
- Navigate to "Jobs" page
- Create job postings with requirements
- System will calculate candidate match scores

## Docker Alternative

If you prefer Docker:
```powershell
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Backend on port 8000
- Frontend on port 3000

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify DATABASE_URL in backend/.env
- Check OpenRouter API key is set

### Frontend won't start
- Run `npm install` in frontend directory
- Check VITE_API_URL in frontend/.env

### Database connection error
- Ensure PostgreSQL is running
- Verify credentials in DATABASE_URL
- Database should be created manually first

## Next Steps

1. **Configure OpenRouter**: Get API key from https://openrouter.ai
2. **Upload test CVs**: Try uploading sample resumes
3. **Explore AI features**: Test the chat functionality
4. **Create jobs**: Add job postings to test matching

## Need Help?

- Check the main README.md for detailed documentation
- API documentation: http://localhost:8000/docs
- OpenRouter docs: https://openrouter.ai/docs

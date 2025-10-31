# ATS/AI Application

A modern Applicant Tracking System with AI-powered CV analysis and natural language querying capabilities.

## 🚀 Features

- **PDF CV Parsing**: Upload PDF resumes and automatically extract text content
- **AI-Powered Analysis**: Automatically analyze CVs using OpenRouter API to extract:
  - Skills and proficiency levels
  - Work experience
  - Education history
  - Professional summary
- **Natural Language Search**: Chat with your database to find candidates using plain English
- **Semantic Matching**: AI-powered candidate-job matching with scores
- **Complete CRUD Operations**: Manage candidates, jobs, and applications
- **Modern UI**: Responsive React frontend with Tailwind CSS
- **RESTful API**: FastAPI backend with automatic API documentation

## 📋 Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database
- **Alembic**: Database migrations
- **PyPDF2/pdfplumber**: PDF text extraction
- **OpenRouter API**: AI/LLM integration

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Axios**: HTTP client

## 🏗️ Project Structure

```
ATS/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── candidates.py
│   │   │           ├── resumes.py
│   │   │           ├── jobs.py
│   │   │           ├── applications.py
│   │   │           └── ai_chat.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── pdf_parser.py
│   │   │   └── matching_service.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Candidates.tsx
│   │   │   ├── CandidateDetail.tsx
│   │   │   ├── Jobs.tsx
│   │   │   ├── JobDetail.tsx
│   │   │   ├── Applications.tsx
│   │   │   ├── AIChat.tsx
│   │   │   └── UploadResume.tsx
│   │   ├── lib/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── docker-compose.yml
```

## 🛠️ Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **OpenRouter API Key** (Get free tier at [openrouter.ai](https://openrouter.ai))

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd ATS
   ```

2. **Create environment file**
   ```powershell
   cp backend/.env.example backend/.env
   ```

3. **Edit backend/.env and add your OpenRouter API key**
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

4. **Start all services**
   ```powershell
   docker-compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```powershell
   cd backend
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```powershell
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Start PostgreSQL**
   Ensure PostgreSQL is running and create a database:
   ```sql
   CREATE DATABASE ats_db;
   ```

6. **Run the backend**
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```powershell
   cd frontend
   ```

2. **Install dependencies**
   ```powershell
   npm install
   ```

3. **Setup environment variables**
   ```powershell
   cp .env.example .env
   # Edit if needed (default points to localhost:8000)
   ```

4. **Start development server**
   ```powershell
   npm run dev
   ```

## 📊 Database Schema

### Core Entities

- **candidates**: Basic candidate information
- **resumes**: Resume files and extracted text
- **skills**: Master list of skills
- **candidate_skills**: Skills linked to candidates with proficiency
- **work_experience**: Employment history
- **education**: Educational background
- **jobs**: Job postings
- **job_skills**: Required/preferred skills for jobs
- **applications**: Job applications and match scores
- **embeddings**: Vector embeddings for semantic search
- **keywords**: Keyword extraction from resumes
- **ai_queries**: Chat history and AI interactions

## 🎯 API Endpoints

### Candidates
- `GET /api/v1/candidates/` - List all candidates
- `POST /api/v1/candidates/` - Create new candidate
- `GET /api/v1/candidates/{id}` - Get candidate details
- `PUT /api/v1/candidates/{id}` - Update candidate
- `DELETE /api/v1/candidates/{id}` - Delete candidate

### Resumes
- `POST /api/v1/resumes/upload/{candidate_id}` - Upload resume
- `GET /api/v1/resumes/candidate/{candidate_id}` - Get candidate resumes
- `GET /api/v1/resumes/{id}` - Get resume details
- `DELETE /api/v1/resumes/{id}` - Delete resume

### Jobs
- `GET /api/v1/jobs/` - List all jobs
- `POST /api/v1/jobs/` - Create new job
- `GET /api/v1/jobs/{id}` - Get job details
- `PUT /api/v1/jobs/{id}` - Update job
- `DELETE /api/v1/jobs/{id}` - Delete job

### Applications
- `GET /api/v1/applications/` - List applications
- `POST /api/v1/applications/` - Create application
- `GET /api/v1/applications/{id}` - Get application details
- `PUT /api/v1/applications/{id}` - Update application

### AI Chat
- `POST /api/v1/ai/chat` - Chat with AI about candidates
- `POST /api/v1/ai/search` - Semantic search for candidates
- `GET /api/v1/ai/queries` - Get query history

## 🤖 AI Features

### Resume Analysis
When a resume is uploaded, the AI automatically:
1. Extracts text from PDF
2. Analyzes content using OpenRouter API
3. Extracts structured data:
   - Skills (technical, soft, languages)
   - Work experience with dates
   - Education with degrees
   - Professional summary

### Natural Language Querying
Ask questions in plain English:
- "Find me Python developers with 5+ years experience"
- "Show candidates with React and Node.js skills"
- "Who has worked at tech companies?"

### Candidate-Job Matching
Automatically calculates match scores based on:
- Required vs. preferred skills
- Years of experience
- Education level
- Location match

## 🔧 Configuration

### Backend Configuration (backend/.env)
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ats_db

# OpenRouter API
OPENROUTER_API_KEY=your_key_here
AI_MODEL=openai/gpt-3.5-turbo

# Application
PROJECT_NAME=ATS/AI Application
API_V1_STR=/api/v1
UPLOAD_DIR=uploads/resumes

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Configuration (frontend/.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📝 Usage Examples

### Upload a Resume
1. Navigate to "Upload Resume" page
2. Fill in candidate information
3. Upload PDF resume file
4. System automatically extracts and analyzes content

### Search for Candidates
1. Go to AI Chat page
2. Type: "Find me candidates with Python experience"
3. Get AI-powered recommendations

### Create Job Posting
1. Navigate to Jobs page
2. Click "Create Job"
3. Fill in job details and requirements
4. System can suggest matching candidates

### Review Applications
1. Go to Applications page
2. See match scores for each application
3. Filter by status or candidate

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**
   - Use strong database passwords
   - Secure API keys
   - Configure proper CORS origins

2. **Database**
   - Use managed PostgreSQL service
   - Enable backups
   - Set up connection pooling

3. **Backend**
   - Use production ASGI server (Gunicorn with Uvicorn workers)
   - Enable HTTPS
   - Set up logging and monitoring

4. **Frontend**
   - Build for production: `npm run build`
   - Serve via CDN or static hosting
   - Configure proper API URLs

## 🧪 Testing

### Backend Tests
```powershell
cd backend
pytest
```

### Frontend Tests
```powershell
cd frontend
npm run test
```

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub.

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)

---

Built with ❤️ using FastAPI, React, and OpenRouter AI

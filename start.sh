#!/usr/bin/env bash
# Render.com start script for backend

echo "🚀 Starting ATS Backend..."

# Run database migrations
echo "📊 Running database setup..."
cd backend
python create_tables.py || echo "⚠️ Tables may already exist"

# Start the application
echo "✅ Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

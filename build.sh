#!/usr/bin/env bash
# Render.com build script for backend

echo "🚀 Starting backend build..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r backend/requirements.txt

echo "✅ Backend build complete!"

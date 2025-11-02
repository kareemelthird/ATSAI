#!/usr/bin/env bash
# Build script for ATS AI application
# Supports both Render.com and local builds

echo "🚀 Starting ATS AI build..."

# Determine deployment target
if [ "$VERCEL" = "1" ]; then
    echo "📍 Building for Vercel deployment..."
    BUILD_TARGET="vercel"
elif [ -n "$RENDER" ]; then
    echo "� Building for Render deployment..."
    BUILD_TARGET="render"
else
    echo "📍 Building for local deployment..."
    BUILD_TARGET="local"
fi

# Install Python dependencies
echo "📦 Installing backend dependencies..."
if [ "$BUILD_TARGET" = "vercel" ]; then
    pip install -r backend/requirements-vercel.txt
else
    pip install -r backend/requirements.txt
fi

echo "✅ Backend build complete!"

# Note: Frontend build is handled separately by each platform

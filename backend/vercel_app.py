import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variable to indicate serverless environment
os.environ['VERCEL'] = '1'

try:
    # Import the FastAPI app
    from app.main import app
    
    # Set up request timeout and limits for serverless
    app.state.is_serverless = True
    
    print("✅ FastAPI app loaded successfully for Vercel")
    
except Exception as e:
    print(f"❌ Error loading FastAPI app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def fallback_root():
        return {"error": "Application failed to load", "detail": str(e)}
    
    @app.get("/api/v1/health")
    def fallback_health():
        return {"status": "error", "message": "App failed to initialize"}

# This is the handler that Vercel will use
# Export the app directly
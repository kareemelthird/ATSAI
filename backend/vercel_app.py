import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now import your FastAPI app
try:
    from app.main import app
    
    # For Vercel, we need to export the app as 'handler'
    def handler(event, context):
        # This is for AWS Lambda compatibility, but Vercel uses different approach
        return app
    
    # Export the app directly for Vercel
    # Vercel will handle the ASGI/WSGI conversion
    
except ImportError as e:
    # Fallback in case of import issues
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="ATS AI - Vercel Fallback")
    
    @app.get("/")
    async def fallback():
        return JSONResponse({
            "status": "error",
            "message": f"Import error: {str(e)}",
            "note": "This is a fallback response. Check your dependencies."
        })

# This is what Vercel will use
application = app
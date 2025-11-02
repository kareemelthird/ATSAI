import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the FastAPI app
from app.main import app

# This is the handler that Vercel will use
# No need for complex wrapper, just export the app directly
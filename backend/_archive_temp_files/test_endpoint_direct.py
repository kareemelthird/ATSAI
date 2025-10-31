"""Direct test of the download endpoint"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test the download endpoint
candidate_id = "92203af8-cb9b-4b87-9a07-e6b049dcb145"
response = client.get(f"/api/v1/candidates/{candidate_id}/resume/download")

print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Content Type: {response.headers.get('content-type')}")

if response.status_code == 200:
    print(f"Content Length: {len(response.content)} bytes")
    # Save the file
    with open("downloaded_cv.pdf", "wb") as f:
        f.write(response.content)
    print("✅ File downloaded successfully!")
else:
    print(f"❌ Error: {response.text}")

import os

# Simulate what the endpoint does
current_file = __file__  # This file
print(f"Current file: {current_file}")

backend_dir = os.path.dirname(current_file)
print(f"Backend dir: {backend_dir}")

relative_path = r"uploads\resumes\92203af8-cb9b-4b87-9a07-e6b049dcb145_Kareem_Hassan_CV.pdf"
absolute_path = os.path.join(backend_dir, relative_path)
print(f"Absolute path: {absolute_path}")
print(f"File exists: {os.path.exists(absolute_path)}")

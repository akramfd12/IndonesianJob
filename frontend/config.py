import os

# Backend URL dari environment variable
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8080"  # fallback kalau jalan lokal
)

API_CHAT = f"{BACKEND_URL}/chat"
API_RESET = f"{BACKEND_URL}/reset"
API_UPLOAD = f"{BACKEND_URL}/upload-cv"
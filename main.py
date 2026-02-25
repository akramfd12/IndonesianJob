import os
from api.routes import app

# =========================================================
# APPLICATION ENTRY POINT
# =========================================================
# This file is used to start the FastAPI application
# using Uvicorn ASGI server.
#
# It allows the app to be run locally or in production
# environments (e.g., Docker, Cloud Run, etc.)
# =========================================================


if __name__ == "__main__":
    # Import uvicorn only when running directly
    # (prevents unnecessary import if used as module)
    import uvicorn

    # Get port from environment variable
    # Default to 8080 if PORT is not set
    # Useful for deployment environments like Docker/Cloud
    port = int(os.environ.get("PORT", 8080))

    # Run FastAPI app using uvicorn
    # host="0.0.0.0" → makes server accessible externally
    # factory=False → app is a direct instance, not a factory function
    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=port,
        factory=False
    )
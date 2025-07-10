"""
Main entry point for the Asynchronous Gemini Chatbot application.

This script starts the FastAPI server using uvicorn with configuration
from the settings module.
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

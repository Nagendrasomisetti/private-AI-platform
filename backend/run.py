"""
Run script for PrivAI backend
"""
import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Server will be available at http://{settings.host}:{settings.port}")
    print(f"API documentation at http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

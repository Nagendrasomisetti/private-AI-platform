"""
PrivAI FastAPI Backend - Simplified Version for Testing
This version runs with minimal dependencies for testing purposes
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json

# Simple configuration
class Settings:
    app_name = "PrivAI"
    app_version = "1.0.0"
    host = "0.0.0.0"
    port = 8000
    debug = True
    log_level = "INFO"

settings = Settings()

# Simple models
class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float

class ErrorResponse(BaseModel):
    error: str
    detail: str

class UploadResponse(BaseModel):
    status: str
    message: str
    file_id: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class DatabaseRequest(BaseModel):
    db_url: str

class DatabaseResponse(BaseModel):
    status: str
    message: str

class IngestResponse(BaseModel):
    status: str
    message: str
    chunks_processed: int

# Application startup time
startup_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 PrivAI backend starting up - Version {settings.app_version}")
    yield
    # Shutdown
    print("🛑 PrivAI backend shutting down")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Privacy-first AI application for college data processing",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Simple in-memory storage for demo
uploaded_files = {}
processed_chunks = []

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic information"""
    uptime = time.time() - startup_time
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime=uptime
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - startup_time
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime=uptime
    )

@app.post("/upload/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (PDF, CSV, DOCX)"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/csv", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Save file
        file_id = f"file_{int(time.time())}"
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store file info
        uploaded_files[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": time.time()
        }
        
        return UploadResponse(
            status="success",
            message=f"File {file.filename} uploaded successfully",
            file_id=file_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/connect-db/", response_model=DatabaseResponse)
async def connect_database(request: DatabaseRequest):
    """Connect to a database (read-only)"""
    try:
        # Simple validation
        if not request.db_url:
            raise HTTPException(status_code=400, detail="Database URL is required")
        
        # Mock database connection test
        if "postgresql://" in request.db_url or "mysql://" in request.db_url or "sqlite://" in request.db_url:
            return DatabaseResponse(
                status="success",
                message="Database connection successful (mock)"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid database URL format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/ingest/", response_model=IngestResponse)
async def ingest_data():
    """Process uploaded files or DB data into chunks"""
    try:
        # Mock ingestion process
        chunks_processed = len(uploaded_files) * 5  # Mock: 5 chunks per file
        
        # Create mock chunks
        for file_id, file_info in uploaded_files.items():
            for i in range(5):
                chunk = {
                    "chunk_id": f"{file_id}_chunk_{i}",
                    "text": f"Mock chunk {i} from {file_info['filename']}",
                    "metadata": {
                        "source_file": file_info['filename'],
                        "chunk_index": i,
                        "file_id": file_id
                    }
                }
                processed_chunks.append(chunk)
        
        return IngestResponse(
            status="success",
            message="Data ingestion completed successfully",
            chunks_processed=chunks_processed
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process user queries and return AI responses"""
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Mock AI response
        answer = f"Mock response to: '{request.query}'. This is a demo response from PrivAI. In the full version, this would use RAG with your uploaded documents."
        
        # Mock sources
        sources = []
        for chunk in processed_chunks[:3]:  # Top 3 chunks
            source = {
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "similarity_score": 0.85,
                "rank": len(sources) + 1
            }
            sources.append(source)
        
        metadata = {
            "query": request.query,
            "retrieved_chunks": len(sources),
            "processing_time": 0.5,
            "model_used": "mock",
            "cached": False
        }
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/files/")
async def list_files():
    """List uploaded files"""
    return {"files": list(uploaded_files.keys()), "count": len(uploaded_files)}

@app.get("/chunks/")
async def list_chunks():
    """List processed chunks"""
    return {"chunks": processed_chunks, "count": len(processed_chunks)}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    print(f"❌ HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"Error occurred at {request.url.path}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    print(f"❌ Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PrivAI Backend (Simplified Version)")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    uvicorn.run(
        "app.main_simple:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

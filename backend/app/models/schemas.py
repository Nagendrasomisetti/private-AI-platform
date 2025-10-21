"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class FileType(str, Enum):
    """Supported file types for upload"""
    PDF = "pdf"
    CSV = "csv"
    DOCX = "docx"


class UploadResponse(BaseModel):
    """Response model for file upload"""
    status: str
    message: str
    file_id: str
    file_name: str
    file_type: FileType
    file_size: int


class DatabaseConnectionRequest(BaseModel):
    """Request model for database connection"""
    db_url: str = Field(..., description="Database connection URL")
    db_type: Optional[str] = Field(None, description="Database type (postgresql, mysql, sqlite)")


class DatabaseConnectionResponse(BaseModel):
    """Response model for database connection"""
    status: str
    message: str
    connection_id: Optional[str] = None
    tables: Optional[List[str]] = None


class IngestRequest(BaseModel):
    """Request model for data ingestion"""
    source_type: str = Field(..., description="Source type: 'files' or 'database'")
    file_ids: Optional[List[str]] = Field(None, description="List of file IDs to ingest")
    connection_id: Optional[str] = Field(None, description="Database connection ID")
    chunk_size: int = Field(1000, description="Chunk size for text splitting")
    chunk_overlap: int = Field(200, description="Overlap between chunks")


class IngestResponse(BaseModel):
    """Response model for data ingestion"""
    status: str
    message: str
    chunks_processed: int
    index_size: int
    processing_time: float


class ChatRequest(BaseModel):
    """Request model for chat queries"""
    query: str = Field(..., description="User query")
    top_k: int = Field(5, description="Number of top chunks to retrieve")
    use_local_llm: bool = Field(True, description="Whether to use local LLM or API fallback")


class ChatResponse(BaseModel):
    """Response model for chat queries"""
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    model_used: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime: float

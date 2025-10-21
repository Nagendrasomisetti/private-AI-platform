"""
Data ingestion API endpoints
"""
import time
from pathlib import Path
from typing import List, Dict, Any

import sqlalchemy
from sqlalchemy import create_engine, text
from fastapi import APIRouter, HTTPException

from ..models.schemas import IngestRequest, IngestResponse, ErrorResponse
from ..core.file_processor import file_processor
from ..core.vector_store import vector_store
from ..core.logging import get_logger
from .database import active_connections

logger = get_logger("ingest_api")
router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/", response_model=IngestResponse)
async def ingest_data(request: IngestRequest):
    """
    Ingest data from files or database into the vector store
    
    Args:
        request: Ingestion request with source type and parameters
        
    Returns:
        IngestResponse: Ingestion status and statistics
    """
    start_time = time.time()
    
    try:
        logger.info("Data ingestion request received", 
                   source_type=request.source_type,
                   chunk_size=request.chunk_size)
        
        documents = []
        
        if request.source_type == "files":
            documents = await _ingest_from_files(request.file_ids or [])
        elif request.source_type == "database":
            documents = await _ingest_from_database(request.connection_id)
        else:
            raise ValueError(f"Unsupported source type: {request.source_type}")
        
        if not documents:
            raise ValueError("No documents found to ingest")
        
        # Add documents to vector store
        vector_store.add_documents(documents)
        
        processing_time = time.time() - start_time
        stats = vector_store.get_stats()
        
        response = IngestResponse(
            status="success",
            message=f"Successfully ingested {len(documents)} documents",
            chunks_processed=len(documents),
            index_size=stats["total_documents"],
            processing_time=processing_time
        )
        
        logger.info("Data ingestion completed successfully",
                   documents_processed=len(documents),
                   processing_time=processing_time,
                   total_index_size=stats["total_documents"])
        
        return response
        
    except ValueError as e:
        logger.error("Data ingestion failed - validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error("Data ingestion failed - unexpected error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")


async def _ingest_from_files(file_ids: List[str]) -> List[Dict[str, Any]]:
    """Ingest data from uploaded files"""
    try:
        documents = []
        upload_dir = Path(file_processor.upload_dir)
        
        for file_id in file_ids:
            # Find the file by ID
            file_path = None
            file_type = None
            
            for ext in [".pdf", ".csv", ".docx"]:
                potential_path = upload_dir / f"{file_id}{ext}"
                if potential_path.exists():
                    file_path = potential_path
                    file_type = ext[1:]  # Remove the dot
                    break
            
            if not file_path or not file_path.exists():
                logger.warning("File not found for ingestion", file_id=file_id)
                continue
            
            # Extract text from file
            text = file_processor.extract_text(str(file_path), file_type)
            
            # Chunk the text
            chunks = file_processor.chunk_text(text, 
                                             chunk_size=1000, 
                                             chunk_overlap=200)
            
            # Create documents for each chunk
            for i, chunk in enumerate(chunks):
                document = {
                    "text": chunk,
                    "metadata": {
                        "file_id": file_id,
                        "file_name": file_path.name,
                        "file_type": file_type,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "source": "file_upload"
                    }
                }
                documents.append(document)
            
            logger.info("File processed for ingestion", 
                       file_id=file_id,
                       file_name=file_path.name,
                       chunks_created=len(chunks))
        
        return documents
        
    except Exception as e:
        logger.error("Failed to ingest from files", error=str(e))
        raise


async def _ingest_from_database(connection_id: str) -> List[Dict[str, Any]]:
    """Ingest data from database connection"""
    try:
        if connection_id not in active_connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        connection_info = active_connections[connection_id]
        engine = create_engine(connection_info["db_url"], echo=False)
        
        documents = []
        
        with engine.connect() as connection:
            # Get all tables
            tables = connection_info["tables"]
            
            for table_name in tables:
                try:
                    # Get table data
                    query = text(f"SELECT * FROM {table_name} LIMIT 1000")  # Limit for safety
                    result = connection.execute(query)
                    rows = result.fetchall()
                    
                    # Convert rows to text
                    if rows:
                        # Get column names
                        columns = result.keys()
                        
                        # Create text representation
                        table_text = f"Table: {table_name}\n"
                        table_text += f"Columns: {', '.join(columns)}\n\n"
                        
                        for i, row in enumerate(rows):
                            row_text = f"Row {i + 1}: "
                            for col in columns:
                                row_text += f"{col}: {row[col]}, "
                            table_text += row_text.rstrip(", ") + "\n"
                        
                        # Chunk the table text
                        chunks = file_processor.chunk_text(table_text, 
                                                         chunk_size=1000, 
                                                         chunk_overlap=200)
                        
                        # Create documents for each chunk
                        for j, chunk in enumerate(chunks):
                            document = {
                                "text": chunk,
                                "metadata": {
                                    "table_name": table_name,
                                    "connection_id": connection_id,
                                    "chunk_index": j,
                                    "total_chunks": len(chunks),
                                    "source": "database",
                                    "row_count": len(rows)
                                }
                            }
                            documents.append(document)
                        
                        logger.info("Table processed for ingestion", 
                                   table_name=table_name,
                                   rows=len(rows),
                                   chunks_created=len(chunks))
                
                except Exception as e:
                    logger.warning("Failed to process table", 
                                 table_name=table_name, 
                                 error=str(e))
                    continue
        
        return documents
        
    except Exception as e:
        logger.error("Failed to ingest from database", error=str(e))
        raise


@router.get("/status")
async def get_ingestion_status():
    """
    Get the current status of the vector store
    
    Returns:
        dict: Vector store statistics
    """
    try:
        logger.info("Ingestion status requested")
        
        stats = vector_store.get_stats()
        
        return {
            "status": "success",
            "vector_store_stats": stats,
            "message": f"Vector store contains {stats['total_documents']} documents"
        }
        
    except Exception as e:
        logger.error("Failed to get ingestion status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get ingestion status")


@router.delete("/clear")
async def clear_vector_store():
    """
    Clear the vector store
    
    Returns:
        dict: Clear operation status
    """
    try:
        logger.info("Vector store clear requested")
        
        vector_store.clear()
        
        logger.info("Vector store cleared successfully")
        
        return {
            "status": "success",
            "message": "Vector store cleared successfully"
        }
        
    except Exception as e:
        logger.error("Failed to clear vector store", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to clear vector store")

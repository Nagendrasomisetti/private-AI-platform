"""
Upload API endpoints for file handling
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from ..models.schemas import UploadResponse, ErrorResponse
from ..core.file_processor import file_processor
from ..core.logging import get_logger

logger = get_logger("upload_api")
router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (PDF, CSV, DOCX) for processing
    
    Args:
        file: The uploaded file
        
    Returns:
        UploadResponse: File upload status and metadata
    """
    try:
        logger.info("File upload request received", filename=file.filename, content_type=file.content_type)
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Save uploaded file
        file_metadata = await file_processor.save_uploaded_file(file)
        
        response = UploadResponse(
            status="success",
            message=f"File '{file.filename}' uploaded successfully",
            file_id=file_metadata["file_id"],
            file_name=file_metadata["filename"],
            file_type=file_metadata["file_type"],
            file_size=file_metadata["file_size"]
        )
        
        logger.info("File uploaded successfully", 
                   file_id=file_metadata["file_id"],
                   filename=file.filename)
        
        return response
        
    except ValueError as e:
        logger.error("File upload validation error", error=str(e), filename=file.filename)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error("File upload failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail="File upload failed")


@router.post("/multiple", response_model=List[UploadResponse])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files at once
    
    Args:
        files: List of uploaded files
        
    Returns:
        List[UploadResponse]: List of upload responses
    """
    try:
        logger.info("Multiple file upload request received", file_count=len(files))
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 10:  # Limit to 10 files per request
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files per request.")
        
        responses = []
        
        for file in files:
            try:
                file_metadata = await file_processor.save_uploaded_file(file)
                response = UploadResponse(
                    status="success",
                    message=f"File '{file.filename}' uploaded successfully",
                    file_id=file_metadata["file_id"],
                    file_name=file_metadata["filename"],
                    file_type=file_metadata["file_type"],
                    file_size=file_metadata["file_size"]
                )
                responses.append(response)
                
            except Exception as e:
                logger.error("Failed to upload individual file", 
                           error=str(e), 
                           filename=file.filename)
                error_response = UploadResponse(
                    status="error",
                    message=f"Failed to upload '{file.filename}': {str(e)}",
                    file_id="",
                    file_name=file.filename,
                    file_type="unknown",
                    file_size=0
                )
                responses.append(error_response)
        
        logger.info("Multiple file upload completed", 
                   total_files=len(files),
                   successful_uploads=len([r for r in responses if r.status == "success"]))
        
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Multiple file upload failed", error=str(e))
        raise HTTPException(status_code=500, detail="Multiple file upload failed")


@router.get("/status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Get the status of an uploaded file
    
    Args:
        file_id: The file ID to check
        
    Returns:
        dict: File status information
    """
    try:
        # This would typically check a database or file system
        # For now, we'll just return a basic status
        logger.info("File status requested", file_id=file_id)
        
        return {
            "file_id": file_id,
            "status": "uploaded",
            "message": "File is ready for processing"
        }
        
    except Exception as e:
        logger.error("Failed to get file status", error=str(e), file_id=file_id)
        raise HTTPException(status_code=500, detail="Failed to get file status")

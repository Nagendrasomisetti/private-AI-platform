"""
File processing utilities for different file types
"""
import io
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
import PyPDF2
from docx import Document
from fastapi import UploadFile

from .config import settings
from .logging import get_logger
from .chunker import FileChunker

logger = get_logger("file_processor")


class FileProcessor:
    """Handles processing of different file types"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chunker = FileChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """Save uploaded file to disk and return metadata"""
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower()
            
            # Validate file extension
            if file_extension not in settings.allowed_extensions:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Create file path
            file_path = self.upload_dir / f"{file_id}{file_extension}"
            
            # Save file
            content = await file.read()
            if len(content) > settings.max_file_size:
                raise ValueError(f"File too large: {len(content)} bytes")
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(
                "File saved successfully",
                file_id=file_id,
                filename=file.filename,
                file_size=len(content)
            )
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "file_type": file_extension[1:]  # Remove the dot
            }
            
        except Exception as e:
            logger.error("Failed to save uploaded file", error=str(e))
            raise
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            logger.info("PDF text extracted", file_path=file_path, text_length=len(text))
            return text.strip()
            
        except Exception as e:
            logger.error("Failed to extract text from PDF", file_path=file_path, error=str(e))
            raise
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            logger.info("DOCX text extracted", file_path=file_path, text_length=len(text))
            return text.strip()
            
        except Exception as e:
            logger.error("Failed to extract text from DOCX", file_path=file_path, error=str(e))
            raise
    
    def extract_text_from_csv(self, file_path: str) -> str:
        """Extract text from CSV file"""
        try:
            # Read CSV and convert to text
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to readable text
            text_parts = []
            
            # Add column headers
            text_parts.append("Columns: " + ", ".join(df.columns.tolist()))
            text_parts.append("\n")
            
            # Add data rows
            for index, row in df.iterrows():
                row_text = f"Row {index + 1}: "
                for col in df.columns:
                    row_text += f"{col}: {row[col]}, "
                text_parts.append(row_text.rstrip(", ") + "\n")
            
            text = "".join(text_parts)
            
            logger.info("CSV text extracted", file_path=file_path, text_length=len(text))
            return text.strip()
            
        except Exception as e:
            logger.error("Failed to extract text from CSV", file_path=file_path, error=str(e))
            raise
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from file based on type"""
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return self.extract_text_from_docx(file_path)
        elif file_type == "csv":
            return self.extract_text_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type for text extraction: {file_type}")
    
    def chunk_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        """Split text into chunks for processing (legacy method)"""
        if chunk_size is None:
            chunk_size = settings.chunk_size
        if chunk_overlap is None:
            chunk_overlap = settings.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
            
            if start >= len(text):
                break
        
        logger.info("Text chunked", total_chunks=len(chunks), chunk_size=chunk_size)
        return chunks
    
    def parse_file_to_chunks(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a file and return chunks with metadata using the advanced chunker.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            logger.info("Parsing file with advanced chunker", file_path=file_path)
            chunks = self.chunker.parse_file(file_path)
            
            logger.info("File parsed successfully", 
                       file_path=file_path, 
                       chunks_created=len(chunks))
            
            return chunks
            
        except Exception as e:
            logger.error("Failed to parse file with chunker", 
                        file_path=file_path, 
                        error=str(e))
            raise


# Global file processor instance
file_processor = FileProcessor()

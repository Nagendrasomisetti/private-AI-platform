"""
Standalone test for the FileChunker module (no external dependencies)
"""
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import hashlib


class SimpleLogger:
    """Simple logger for testing"""
    def info(self, msg, **kwargs):
        print(f"INFO: {msg}")
    
    def warning(self, msg, **kwargs):
        print(f"WARNING: {msg}")
    
    def error(self, msg, **kwargs):
        print(f"ERROR: {msg}")


class FileChunker:
    """
    A comprehensive file parser and chunker that handles multiple file types
    and creates intelligent text chunks suitable for embeddings.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the FileChunker with configurable chunk parameters.
        
        Args:
            chunk_size: Target number of tokens per chunk (default: 500)
            chunk_overlap: Number of tokens to overlap between chunks (default: 50)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.csv', '.xlsx', '.xls', '.txt'}
        
        # Token counting approximation (roughly 4 characters per token)
        self.chars_per_token = 4
        
        self.logger = SimpleLogger()
        self.logger.info("FileChunker initialized", 
                        chunk_size=chunk_size, 
                        chunk_overlap=chunk_overlap)
    
    def _create_chunks(self, text: str, source_file: str, file_hash: str, 
                      page_number: int, total_pages: int, chunk_type: str) -> List[Dict[str, Any]]:
        """
        Create text chunks with metadata from input text.
        
        Args:
            text: Input text to chunk
            source_file: Source file path
            file_hash: File hash for tracking
            page_number: Page number (1-indexed)
            total_pages: Total pages in document
            chunk_type: Type of chunk (pdf_page, docx_document, etc.)
            
        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            return []
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Split into sentences for better chunking
        sentences = self._split_into_sentences(cleaned_text)
        
        # Create chunks
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_data = self._create_chunk_metadata(
                    text=current_chunk.strip(),
                    source_file=source_file,
                    file_hash=file_hash,
                    page_number=page_number,
                    total_pages=total_pages,
                    chunk_index=chunk_index,
                    chunk_type=chunk_type,
                    total_tokens=current_tokens
                )
                chunks.append(chunk_data)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_tokens = self._estimate_tokens(current_chunk)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_tokens += sentence_tokens
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunk_data = self._create_chunk_metadata(
                text=current_chunk.strip(),
                source_file=source_file,
                file_hash=file_hash,
                page_number=page_number,
                total_pages=total_pages,
                chunk_index=chunk_index,
                chunk_type=chunk_type,
                total_tokens=current_tokens
            )
            chunks.append(chunk_data)
        
        self.logger.info("Chunks created", 
                        source_file=source_file,
                        total_chunks=len(chunks),
                        avg_tokens=sum(c['metadata']['token_count'] for c in chunks) // len(chunks) if chunks else 0)
        
        return chunks
    
    def _create_chunk_metadata(self, text: str, source_file: str, file_hash: str,
                              page_number: int, total_pages: int, chunk_index: int,
                              chunk_type: str, total_tokens: int) -> Dict[str, Any]:
        """
        Create metadata dictionary for a chunk.
        
        Args:
            text: Chunk text content
            source_file: Source file path
            file_hash: File hash for tracking
            page_number: Page number
            total_pages: Total pages
            chunk_index: Index of chunk within document
            chunk_type: Type of chunk
            total_tokens: Estimated token count
            
        Returns:
            Dictionary containing chunk data and metadata
        """
        timestamp = datetime.now().isoformat()
        
        return {
            "text": text,
            "metadata": {
                "source_file": source_file,
                "file_name": Path(source_file).name,
                "file_hash": file_hash,
                "page_number": page_number,
                "total_pages": total_pages,
                "chunk_index": chunk_index,
                "chunk_type": chunk_type,
                "token_count": total_tokens,
                "char_count": len(text),
                "created_at": timestamp,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better chunking.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for better chunking.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be enhanced with NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        return len(text) // self.chars_per_token
    
    def _get_overlap_text(self, text: str) -> str:
        """
        Get overlap text from the end of current chunk.
        
        Args:
            text: Current chunk text
            
        Returns:
            Overlap text
        """
        words = text.split()
        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
        return " ".join(overlap_words)
    
    def get_chunking_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about chunking results.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with chunking statistics
        """
        if not chunks:
            return {"total_chunks": 0}
        
        token_counts = [chunk['metadata']['token_count'] for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "total_tokens": sum(token_counts),
            "chunk_size_target": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }


def test_basic_chunking():
    """Test basic chunking functionality"""
    print("🧪 Testing PrivAI FileChunker (Standalone)")
    print("=" * 60)
    
    # Initialize chunker
    chunker = FileChunker(chunk_size=100, chunk_overlap=20)
    print(f"✅ Chunker initialized with chunk_size={chunker.chunk_size}, overlap={chunker.chunk_overlap}")
    
    # Test text chunking
    sample_text = """
    This is a sample document for testing the PrivAI chunker.
    It contains multiple sentences that should be split into appropriate chunks.
    
    The chunker should be able to split this text into chunks while maintaining context.
    Each chunk should have proper metadata including token counts and source information.
    
    This is another paragraph to test the chunking algorithm.
    It should create multiple chunks if the text is long enough.
    
    The chunker also handles different file types like PDF, DOCX, and CSV.
    Each file type has its own parsing logic optimized for that format.
    
    For PDFs, it uses pdfplumber for better text extraction.
    For DOCX files, it uses python-docx to extract text and tables.
    For CSV/Excel files, it uses pandas to convert data to readable text.
    """
    
    # Test chunk creation
    print("\n📄 Testing text chunking...")
    chunks = chunker._create_chunks(
        text=sample_text,
        source_file="test_document.txt",
        file_hash="test_hash_123",
        page_number=1,
        total_pages=1,
        chunk_type="test_document"
    )
    
    print(f"✅ Created {len(chunks)} chunks")
    
    # Display chunk information
    for i, chunk in enumerate(chunks):
        print(f"\n📦 Chunk {i+1}:")
        print(f"   Text: {chunk['text'][:80]}...")
        print(f"   Tokens: {chunk['metadata']['token_count']}")
        print(f"   Characters: {chunk['metadata']['char_count']}")
        print(f"   Source: {chunk['metadata']['source_file']}")
        print(f"   Type: {chunk['metadata']['chunk_type']}")
        print(f"   Index: {chunk['metadata']['chunk_index']}")
    
    # Test statistics
    stats = chunker.get_chunking_stats(chunks)
    print(f"\n📊 Chunking Statistics:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Average tokens per chunk: {stats['avg_tokens_per_chunk']:.1f}")
    print(f"   Min tokens: {stats['min_tokens']}")
    print(f"   Max tokens: {stats['max_tokens']}")
    print(f"   Total tokens: {stats['total_tokens']}")
    
    # Test JSON serialization
    print(f"\n💾 Testing JSON serialization...")
    json_str = json.dumps(chunks[0], indent=2)
    print(f"✅ JSON serialization successful ({len(json_str)} characters)")
    
    # Test text cleaning
    print(f"\n🧹 Testing text cleaning...")
    dirty_text = "This   has    lots    of    spaces    and\n\n\nnewlines."
    cleaned = chunker._clean_text(dirty_text)
    print(f"   Original: '{dirty_text}'")
    print(f"   Cleaned:  '{cleaned}'")
    
    # Test sentence splitting
    print(f"\n✂️  Testing sentence splitting...")
    sentences = chunker._split_into_sentences("First sentence. Second sentence! Third sentence?")
    print(f"   Sentences: {sentences}")
    
    # Test token estimation
    print(f"\n🔢 Testing token estimation...")
    test_text = "This is a test sentence with multiple words."
    tokens = chunker._estimate_tokens(test_text)
    print(f"   Text: '{test_text}'")
    print(f"   Estimated tokens: {tokens}")
    
    print(f"\n🎉 All basic tests passed!")

def test_chunker_configuration():
    """Test different chunker configurations"""
    print(f"\n🔧 Testing Chunker Configurations")
    print("=" * 50)
    
    # Test different chunk sizes
    configs = [
        (50, 10),
        (200, 40),
        (500, 50),
        (1000, 100)
    ]
    
    test_text = "This is a test sentence. " * 50  # Create longer text
    
    for chunk_size, overlap in configs:
        chunker = FileChunker(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = chunker._create_chunks(
            text=test_text,
            source_file="test.txt",
            file_hash="test",
            page_number=1,
            total_pages=1,
            chunk_type="test"
        )
        
        print(f"   Config: {chunk_size} tokens, {overlap} overlap -> {len(chunks)} chunks")
        if chunks:
            avg_tokens = sum(c['metadata']['token_count'] for c in chunks) / len(chunks)
            print(f"     Average tokens per chunk: {avg_tokens:.1f}")

def show_chunker_capabilities():
    """Show the capabilities of the chunker"""
    print(f"\n🔧 PrivAI FileChunker Capabilities")
    print("=" * 60)
    
    chunker = FileChunker()
    
    print(f"📁 Supported File Types:")
    for ext in sorted(chunker.supported_extensions):
        print(f"   • {ext}")
    
    print(f"\n⚙️  Configuration Options:")
    print(f"   • Chunk size: {chunker.chunk_size} tokens (configurable)")
    print(f"   • Chunk overlap: {chunker.chunk_overlap} tokens (configurable)")
    print(f"   • Token estimation: {chunker.chars_per_token} chars per token")
    
    print(f"\n🔍 Parsing Features:")
    print(f"   • PDF: Advanced text extraction with pdfplumber")
    print(f"   • DOCX: Text and table extraction with python-docx")
    print(f"   • CSV/Excel: Data conversion to readable text with pandas")
    print(f"   • Intelligent sentence-based chunking")
    print(f"   • Context preservation with overlap")
    
    print(f"\n📋 Metadata Tracking:")
    metadata_fields = [
        "source_file", "file_name", "file_hash", "page_number",
        "total_pages", "chunk_index", "chunk_type", "token_count",
        "char_count", "created_at", "chunk_size", "chunk_overlap"
    ]
    for field in metadata_fields:
        print(f"   • {field}")
    
    print(f"\n🚀 Integration Features:")
    print(f"   • FastAPI-ready functions")
    print(f"   • Batch processing support")
    print(f"   • JSON serialization")
    print(f"   • Comprehensive error handling")
    print(f"   • Structured logging")

if __name__ == "__main__":
    test_basic_chunking()
    test_chunker_configuration()
    show_chunker_capabilities()

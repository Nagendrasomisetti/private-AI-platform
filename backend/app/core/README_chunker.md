# PrivAI FileChunker Module

A comprehensive file parser and chunker for PrivAI that handles multiple file types and creates intelligent text chunks suitable for embeddings.

## Features

### 📁 **Multi-Format Support**
- **PDF**: Uses `pdfplumber` for advanced text extraction and table handling
- **DOCX**: Uses `python-docx` for text and table extraction
- **CSV/Excel**: Uses `pandas` for data conversion to readable text
- **Text**: Built-in text processing with intelligent chunking

### 🧠 **Intelligent Chunking**
- **Token-based chunking**: Configurable chunk size (default: 500 tokens)
- **Overlap preservation**: Maintains context with configurable overlap (default: 50 tokens)
- **Sentence-aware splitting**: Splits at sentence boundaries for better coherence
- **Smart text cleaning**: Removes excessive whitespace and normalizes text

### 📊 **Comprehensive Metadata**
Each chunk includes detailed metadata:
- `source_file`: Original file path
- `file_name`: Just the filename
- `file_hash`: MD5 hash for tracking
- `page_number`: Page number (for PDFs)
- `total_pages`: Total pages in document
- `chunk_index`: Position within document
- `chunk_type`: Type of content (pdf_page, docx_document, etc.)
- `token_count`: Estimated token count
- `char_count`: Character count
- `created_at`: Timestamp
- `chunk_size`: Target chunk size used
- `chunk_overlap`: Overlap size used

## Usage

### Basic Usage

```python
from app.core.chunker import FileChunker

# Initialize chunker
chunker = FileChunker(chunk_size=500, chunk_overlap=50)

# Parse a file
chunks = chunker.parse_file("document.pdf")

# Each chunk is a dictionary with 'text' and 'metadata' keys
for chunk in chunks:
    print(f"Text: {chunk['text'][:100]}...")
    print(f"Tokens: {chunk['metadata']['token_count']}")
    print(f"Source: {chunk['metadata']['source_file']}")
```

### Convenience Functions

```python
from app.core.chunker import parse_file_to_chunks, parse_multiple_files

# Parse single file
chunks = parse_file_to_chunks("document.pdf", chunk_size=300, chunk_overlap=30)

# Parse multiple files
all_chunks = parse_multiple_files(["doc1.pdf", "doc2.docx", "data.csv"])
```

### FastAPI Integration

```python
from app.core.file_processor import file_processor

# Use the integrated file processor
chunks = file_processor.parse_file_to_chunks("uploaded_file.pdf")
```

## Configuration

The chunker can be configured with different parameters:

```python
chunker = FileChunker(
    chunk_size=500,      # Target tokens per chunk
    chunk_overlap=50     # Token overlap between chunks
)
```

## File Type Details

### PDF Processing
- Uses `pdfplumber` for better text extraction than PyPDF2
- Handles tables and complex layouts
- Extracts text from each page separately
- Preserves page numbers in metadata

### DOCX Processing
- Extracts text from paragraphs
- Handles tables and converts to readable format
- Preserves document structure
- Works with both .docx and .doc files

### CSV/Excel Processing
- Converts data to readable text format
- Includes column information and data types
- Shows sample data (first 10 rows)
- Provides summary statistics for numeric columns

## Error Handling

The chunker includes comprehensive error handling:
- File validation (existence, supported types)
- Graceful handling of parsing errors
- Detailed logging for debugging
- Fallback mechanisms for problematic files

## Performance

- **Token estimation**: ~4 characters per token (configurable)
- **Memory efficient**: Processes files incrementally
- **Fast processing**: Optimized for large documents
- **Parallel ready**: Can be used in async contexts

## Examples

See `examples/chunker_examples.py` for comprehensive usage examples including:
- Different file type processing
- Metadata inspection
- Statistics and analysis
- JSON serialization
- Batch processing

## Dependencies

- `pdfplumber`: PDF text extraction
- `python-docx`: DOCX file processing
- `pandas`: CSV/Excel data handling
- `pathlib`: File path handling
- `hashlib`: File hashing for tracking

## Integration

The chunker integrates seamlessly with:
- **FastAPI backend**: Via `file_processor.parse_file_to_chunks()`
- **Vector store**: Chunks are ready for embedding generation
- **Database storage**: Metadata supports tracking and retrieval
- **API responses**: JSON serializable for API endpoints

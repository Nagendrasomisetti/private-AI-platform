"""
Test script for the FileChunker module
"""
import json
from pathlib import Path
from app.core.chunker import FileChunker, parse_file_to_chunks, parse_multiple_files

def test_chunker():
    """Test the FileChunker functionality"""
    print("🧪 Testing PrivAI FileChunker")
    print("=" * 50)
    
    # Initialize chunker
    chunker = FileChunker(chunk_size=500, chunk_overlap=50)
    print(f"✅ Chunker initialized with chunk_size={chunker.chunk_size}, overlap={chunker.chunk_overlap}")
    
    # Test with a sample text file
    sample_text = """
    This is a sample document for testing the PrivAI chunker.
    It contains multiple paragraphs with various content.
    
    The chunker should be able to split this text into appropriate chunks
    while maintaining context and providing proper metadata.
    
    Each chunk should have information about its source, position,
    and other relevant metadata for embedding generation.
    
    This is another paragraph to test the chunking algorithm.
    It should create multiple chunks if the text is long enough.
    
    The chunker also handles different file types like PDF, DOCX, and CSV.
    Each file type has its own parsing logic optimized for that format.
    
    For PDFs, it uses pdfplumber for better text extraction.
    For DOCX files, it uses python-docx to extract text and tables.
    For CSV/Excel files, it uses pandas to convert data to readable text.
    """
    
    # Create a temporary test file
    test_file = Path("test_document.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    try:
        # Test chunking
        print("\n📄 Testing text chunking...")
        chunks = chunker._create_chunks(
            text=sample_text,
            source_file=str(test_file),
            file_hash="test_hash_123",
            page_number=1,
            total_pages=1,
            chunk_type="test_document"
        )
        
        print(f"✅ Created {len(chunks)} chunks")
        
        # Display chunk information
        for i, chunk in enumerate(chunks):
            print(f"\n📦 Chunk {i+1}:")
            print(f"   Text: {chunk['text'][:100]}...")
            print(f"   Tokens: {chunk['metadata']['token_count']}")
            print(f"   Characters: {chunk['metadata']['char_count']}")
            print(f"   Source: {chunk['metadata']['source_file']}")
            print(f"   Type: {chunk['metadata']['chunk_type']}")
        
        # Test statistics
        stats = chunker.get_chunking_stats(chunks)
        print(f"\n📊 Chunking Statistics:")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Average tokens per chunk: {stats['avg_tokens_per_chunk']:.1f}")
        print(f"   Min tokens: {stats['min_tokens']}")
        print(f"   Max tokens: {stats['max_tokens']}")
        print(f"   Total tokens: {stats['total_tokens']}")
        
        # Test convenience functions
        print(f"\n🔧 Testing convenience functions...")
        chunks2 = parse_file_to_chunks(test_file, chunk_size=300, chunk_overlap=30)
        print(f"✅ Convenience function created {len(chunks2)} chunks")
        
        # Test multiple files
        test_file2 = Path("test_document2.txt")
        with open(test_file2, "w", encoding="utf-8") as f:
            f.write("This is a second test document with different content.")
        
        all_chunks = parse_multiple_files([test_file, test_file2])
        print(f"✅ Multiple files parsing created {len(all_chunks)} total chunks")
        
        # Test JSON serialization (important for API responses)
        print(f"\n💾 Testing JSON serialization...")
        json_str = json.dumps(chunks[0], indent=2)
        print(f"✅ JSON serialization successful ({len(json_str)} characters)")
        
        print(f"\n🎉 All tests passed!")
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if Path("test_document2.txt").exists():
            Path("test_document2.txt").unlink()
        print(f"\n🧹 Cleanup completed")

def demonstrate_file_types():
    """Demonstrate chunker with different file types"""
    print("\n" + "=" * 50)
    print("📁 File Type Support Demonstration")
    print("=" * 50)
    
    chunker = FileChunker()
    
    # Show supported extensions
    print(f"✅ Supported file extensions: {', '.join(sorted(chunker.supported_extensions))}")
    
    # Show chunker configuration
    print(f"✅ Chunk size: {chunker.chunk_size} tokens")
    print(f"✅ Chunk overlap: {chunker.chunk_overlap} tokens")
    print(f"✅ Characters per token estimate: {chunker.chars_per_token}")
    
    print(f"\n📋 File Type Capabilities:")
    print(f"   📄 PDF: Uses pdfplumber for better text extraction, handles tables")
    print(f"   📝 DOCX: Uses python-docx, extracts text and tables")
    print(f"   📊 CSV/Excel: Uses pandas, converts to readable text format")
    print(f"   🔍 All types: Intelligent sentence-based chunking with overlap")

if __name__ == "__main__":
    test_chunker()
    demonstrate_file_types()

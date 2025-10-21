"""
Simple test script for the FileChunker module (without external dependencies)
"""
import json
from pathlib import Path
from app.core.chunker import FileChunker

def test_basic_chunking():
    """Test basic chunking functionality without file I/O"""
    print("🧪 Testing PrivAI FileChunker (Basic)")
    print("=" * 50)
    
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

if __name__ == "__main__":
    test_basic_chunking()
    test_chunker_configuration()

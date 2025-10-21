"""
Test script for the Embeddings module
"""
import json
import numpy as np
from pathlib import Path
from app.core.embeddings import EmbeddingGenerator, generate_embeddings_for_chunks, generate_query_embedding

def test_embeddings():
    """Test the embeddings functionality"""
    print("🧪 Testing PrivAI Embeddings Module")
    print("=" * 50)
    
    # Create sample chunks
    sample_chunks = [
        {
            "text": "PrivAI is a privacy-first AI application for college data processing.",
            "metadata": {
                "source_file": "test1.txt",
                "chunk_index": 0,
                "chunk_type": "document",
                "token_count": 15
            }
        },
        {
            "text": "The application uses advanced natural language processing techniques.",
            "metadata": {
                "source_file": "test1.txt", 
                "chunk_index": 1,
                "chunk_type": "document",
                "token_count": 12
            }
        },
        {
            "text": "All data processing happens locally to ensure privacy and security.",
            "metadata": {
                "source_file": "test1.txt",
                "chunk_index": 2, 
                "chunk_type": "document",
                "token_count": 14
            }
        },
        {
            "text": "Students can upload documents and ask questions about their content.",
            "metadata": {
                "source_file": "test2.txt",
                "chunk_index": 0,
                "chunk_type": "document", 
                "token_count": 13
            }
        },
        {
            "text": "The system provides intelligent answers based on document analysis.",
            "metadata": {
                "source_file": "test2.txt",
                "chunk_index": 1,
                "chunk_type": "document",
                "token_count": 12
            }
        }
    ]
    
    try:
        # Test 1: Initialize embedding generator
        print("\n🔧 Test 1: Initialize Embedding Generator")
        print("-" * 40)
        
        generator = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2",
            device="cpu",
            use_quantization=False
        )
        
        print(f"✅ Generator initialized")
        print(f"   Model: {generator.model_name}")
        print(f"   Device: {generator.device}")
        print(f"   Embedding dimension: {generator.embedding_dim}")
        
        # Test 2: Generate embeddings
        print(f"\n📊 Test 2: Generate Embeddings")
        print("-" * 40)
        
        chunks_with_embeddings = generator.generate_embeddings(sample_chunks)
        
        print(f"✅ Generated embeddings for {len(chunks_with_embeddings)} chunks")
        
        # Show embedding details
        for i, chunk in enumerate(chunks_with_embeddings):
            embedding = chunk.get('embedding')
            if embedding is not None:
                print(f"   Chunk {i+1}: {chunk['text'][:50]}...")
                print(f"     Embedding shape: {embedding.shape}")
                print(f"     Embedding norm: {np.linalg.norm(embedding):.4f}")
        
        # Test 3: Similarity computation
        print(f"\n🔍 Test 3: Similarity Computation")
        print("-" * 40)
        
        if len(chunks_with_embeddings) >= 2:
            emb1 = chunks_with_embeddings[0]['embedding']
            emb2 = chunks_with_embeddings[1]['embedding']
            
            similarity = generator.compute_similarity(emb1, emb2)
            print(f"✅ Similarity between chunk 1 and 2: {similarity:.4f}")
            
            # Test self-similarity
            self_similarity = generator.compute_similarity(emb1, emb1)
            print(f"✅ Self-similarity (should be 1.0): {self_similarity:.4f}")
        
        # Test 4: Query similarity search
        print(f"\n🔎 Test 4: Query Similarity Search")
        print("-" * 40)
        
        query = "How does PrivAI ensure privacy?"
        query_embedding = generate_query_embedding(query)
        
        print(f"✅ Generated query embedding for: '{query}'")
        print(f"   Query embedding shape: {query_embedding.shape}")
        
        # Find similar chunks
        similar_chunks = generator.find_similar_chunks(
            query_embedding, 
            chunks_with_embeddings, 
            top_k=3
        )
        
        print(f"✅ Found {len(similar_chunks)} similar chunks:")
        for i, chunk in enumerate(similar_chunks):
            print(f"   {i+1}. Similarity: {chunk['similarity_score']:.4f}")
            print(f"      Text: {chunk['text'][:60]}...")
        
        # Test 5: Batch processing
        print(f"\n⚡ Test 5: Batch Processing")
        print("-" * 40)
        
        # Test with different batch sizes
        batch_sizes = [1, 2, 5]
        for batch_size in batch_sizes:
            chunks_batch = generator.generate_embeddings(
                sample_chunks[:3], 
                batch_size=batch_size,
                use_cache=False
            )
            print(f"   Batch size {batch_size}: {len(chunks_batch)} chunks processed")
        
        # Test 6: Caching
        print(f"\n💾 Test 6: Embedding Caching")
        print("-" * 40)
        
        # First run (no cache)
        chunks_cached = generator.generate_embeddings(sample_chunks[:2], use_cache=True)
        print(f"✅ First run: {len(chunks_cached)} chunks processed")
        
        # Second run (with cache)
        chunks_cached_2 = generator.generate_embeddings(sample_chunks[:2], use_cache=True)
        print(f"✅ Second run (cached): {len(chunks_cached_2)} chunks processed")
        
        # Test 7: Statistics
        print(f"\n📈 Test 7: Generator Statistics")
        print("-" * 40)
        
        stats = generator.get_embedding_stats()
        print(f"✅ Generator statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 8: Convenience functions
        print(f"\n🛠️  Test 8: Convenience Functions")
        print("-" * 40)
        
        # Test convenience function
        convenience_chunks = generate_embeddings_for_chunks(sample_chunks[:2])
        print(f"✅ Convenience function: {len(convenience_chunks)} chunks processed")
        
        # Test JSON serialization
        print(f"\n💾 Test 9: JSON Serialization")
        print("-" * 40)
        
        # Convert numpy arrays to lists for JSON serialization
        json_ready_chunks = []
        for chunk in chunks_with_embeddings[:2]:
            json_chunk = chunk.copy()
            if 'embedding' in json_chunk:
                json_chunk['embedding'] = json_chunk['embedding'].tolist()
            json_ready_chunks.append(json_chunk)
        
        json_str = json.dumps(json_ready_chunks, indent=2)
        print(f"✅ JSON serialization successful ({len(json_str)} characters)")
        
        print(f"\n🎉 All embedding tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install sentence-transformers: pip install sentence-transformers")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_embedding_quality():
    """Test embedding quality with different text types"""
    print(f"\n🔬 Testing Embedding Quality")
    print("=" * 50)
    
    try:
        generator = EmbeddingGenerator()
        
        # Test with different types of text
        test_texts = [
            "PrivAI is a privacy-first AI application.",
            "The system processes documents locally.",
            "Students can ask questions about their data.",
            "Machine learning algorithms analyze text content.",
            "Vector embeddings enable semantic search.",
            "Privacy is maintained through local processing.",
            "Natural language processing extracts meaning.",
            "Document analysis provides intelligent insights."
        ]
        
        # Create chunks
        chunks = []
        for i, text in enumerate(test_texts):
            chunks.append({
                "text": text,
                "metadata": {
                    "chunk_index": i,
                    "chunk_type": "test"
                }
            })
        
        # Generate embeddings
        chunks_with_embeddings = generator.generate_embeddings(chunks)
        
        print(f"✅ Generated embeddings for {len(chunks_with_embeddings)} test texts")
        
        # Test semantic similarity
        print(f"\n📊 Semantic Similarity Analysis:")
        
        # Find most similar pairs
        similarities = []
        for i in range(len(chunks_with_embeddings)):
            for j in range(i+1, len(chunks_with_embeddings)):
                emb1 = chunks_with_embeddings[i]['embedding']
                emb2 = chunks_with_embeddings[j]['embedding']
                similarity = generator.compute_similarity(emb1, emb2)
                similarities.append((i, j, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        print(f"   Top 3 most similar pairs:")
        for i, (idx1, idx2, sim) in enumerate(similarities[:3]):
            text1 = chunks_with_embeddings[idx1]['text']
            text2 = chunks_with_embeddings[idx2]['text']
            print(f"   {i+1}. Similarity: {sim:.4f}")
            print(f"      '{text1}'")
            print(f"      '{text2}'")
        
        print(f"\n🎉 Embedding quality tests completed!")
        
    except Exception as e:
        print(f"❌ Quality test failed: {e}")

if __name__ == "__main__":
    test_embeddings()
    test_embedding_quality()

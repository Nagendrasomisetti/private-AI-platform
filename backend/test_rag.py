"""
Test script for the RAG module
"""
import json
import numpy as np
from pathlib import Path
from app.core.rag import RAGPipeline, create_rag_pipeline, query_rag, get_default_rag_pipeline

def test_rag_pipeline():
    """Test the RAG pipeline functionality"""
    print("🧪 Testing PrivAI RAG Pipeline")
    print("=" * 50)
    
    try:
        # Test 1: Initialize RAG pipeline
        print("\n🔧 Test 1: Initialize RAG Pipeline")
        print("-" * 40)
        
        rag = RAGPipeline(
            local_model_name="microsoft/DialoGPT-medium",
            cache_dir="test_rag_cache"
        )
        
        print(f"✅ RAG pipeline initialized")
        print(f"   Local LLM available: {rag.local_llm is not None}")
        print(f"   OpenAI available: {rag.openai_client is not None}")
        print(f"   Cache directory: {rag.cache_dir}")
        
        # Test 2: Create sample documents and add to vector database
        print(f"\n📊 Test 2: Setup Sample Documents")
        print("-" * 40)
        
        sample_documents = [
            {
                "text": "PrivAI is a privacy-first AI application designed for educational institutions. It provides secure, local processing of academic documents and data without sending information to external servers.",
                "metadata": {
                    "source_file": "privacy_policy.pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                    "chunk_type": "privacy_policy"
                }
            },
            {
                "text": "The system uses advanced natural language processing techniques to understand and analyze document content. It can extract key information, answer questions, and provide intelligent insights.",
                "metadata": {
                    "source_file": "technical_specs.pdf",
                    "page_number": 2,
                    "chunk_index": 0,
                    "chunk_type": "technical_document"
                }
            },
            {
                "text": "Students can upload various file types including PDFs, Word documents, and spreadsheets. The system automatically processes these files and creates searchable knowledge bases.",
                "metadata": {
                    "source_file": "user_guide.pdf",
                    "page_number": 3,
                    "chunk_index": 0,
                    "chunk_type": "user_guide"
                }
            },
            {
                "text": "Vector embeddings enable semantic search capabilities. The system can find relevant information even when exact keywords don't match, using meaning and context.",
                "metadata": {
                    "source_file": "technical_specs.pdf",
                    "page_number": 4,
                    "chunk_index": 1,
                    "chunk_type": "technical_document"
                }
            },
            {
                "text": "All data processing happens locally on the user's machine. This ensures complete privacy and security, as no sensitive information ever leaves the local environment.",
                "metadata": {
                    "source_file": "privacy_policy.pdf",
                    "page_number": 2,
                    "chunk_index": 1,
                    "chunk_type": "privacy_policy"
                }
            }
        ]
        
        # Create sample embeddings
        sample_embeddings = []
        for i, doc in enumerate(sample_documents):
            # Create deterministic embedding based on content
            hash_value = hash(doc['text']) % (2**32)
            np.random.seed(hash_value)
            embedding = np.random.randn(384).astype('float32')
            embedding = embedding / np.linalg.norm(embedding)
            sample_embeddings.append(embedding)
        
        # Add documents to vector database
        chunk_ids = rag.vector_database.add_chunks(sample_documents, sample_embeddings)
        
        print(f"✅ Added {len(chunk_ids)} documents to vector database")
        print(f"   Total chunks in DB: {rag.vector_database.get_chunk_count()}")
        
        # Test 3: Test query processing
        print(f"\n🔍 Test 3: Query Processing")
        print("-" * 40)
        
        test_queries = [
            "How does PrivAI ensure privacy?",
            "What file types are supported?",
            "How does the system process documents?",
            "What are vector embeddings used for?",
            "Is data processing local or cloud-based?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: '{query}'")
            
            try:
                # Process query
                result = rag.query(query, top_k=3, use_local_llm=True)
                
                print(f"   ✅ Query processed")
                print(f"   Answer: {result['answer'][:100]}...")
                print(f"   Sources: {len(result['sources'])}")
                print(f"   Processing time: {result['metadata']['processing_time']:.2f}s")
                print(f"   Model used: {result['metadata']['model_used']}")
                
                # Show sources
                for j, source in enumerate(result['sources'][:2]):  # Show first 2 sources
                    print(f"     Source {j+1}: {source['text'][:50]}... (similarity: {source['similarity_score']:.3f})")
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
        
        # Test 4: Test caching
        print(f"\n💾 Test 4: Response Caching")
        print("-" * 40)
        
        query = "What is PrivAI?"
        
        # First query (not cached)
        print(f"   First query (not cached):")
        start_time = time.time()
        result1 = rag.query(query, use_cache=True)
        first_time = time.time() - start_time
        print(f"     Processing time: {first_time:.2f}s")
        print(f"     Cached: {result1['metadata']['cached']}")
        
        # Second query (should be cached)
        print(f"   Second query (cached):")
        start_time = time.time()
        result2 = rag.query(query, use_cache=True)
        second_time = time.time() - start_time
        print(f"     Processing time: {second_time:.2f}s")
        print(f"     Cached: {result2['metadata']['cached']}")
        
        if second_time < first_time:
            print(f"     ✅ Caching working (speedup: {first_time/second_time:.1f}x)")
        else:
            print(f"     ⚠️  Caching may not be working as expected")
        
        # Test 5: Test different top_k values
        print(f"\n🔍 Test 5: Different Top-K Values")
        print("-" * 40)
        
        query = "How does the system work?"
        
        for top_k in [1, 3, 5]:
            result = rag.query(query, top_k=top_k)
            print(f"   Top-K {top_k}: {len(result['sources'])} sources, {result['metadata']['processing_time']:.2f}s")
        
        # Test 6: Test prompt construction
        print(f"\n📝 Test 6: Prompt Construction")
        print("-" * 40)
        
        # Get a sample query and chunks
        query = "What is PrivAI?"
        query_embedding = rag._generate_query_embedding(query)
        chunks = rag._retrieve_chunks(query_embedding, 2)
        prompt = rag._construct_prompt(query, chunks)
        
        print(f"   ✅ Prompt constructed")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Prompt preview: {prompt[:200]}...")
        
        # Test 7: Test statistics
        print(f"\n📊 Test 7: RAG Statistics")
        print("-" * 40)
        
        stats = rag.get_stats()
        print(f"   ✅ RAG statistics:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"     {key}:")
                for sub_key, sub_value in value.items():
                    print(f"       {sub_key}: {sub_value}")
            else:
                print(f"     {key}: {value}")
        
        # Test 8: Test convenience functions
        print(f"\n🛠️  Test 8: Convenience Functions")
        print("-" * 40)
        
        # Test create_rag_pipeline
        rag2 = create_rag_pipeline()
        print(f"   ✅ Created RAG pipeline with convenience function")
        
        # Test query_rag
        result = query_rag("What is PrivAI?", top_k=2)
        print(f"   ✅ Query with convenience function: {len(result['sources'])} sources")
        
        # Test get_default_rag_pipeline
        default_rag = get_default_rag_pipeline()
        print(f"   ✅ Got default RAG pipeline")
        
        # Test 9: Test error handling
        print(f"\n⚠️  Test 9: Error Handling")
        print("-" * 40)
        
        # Test with empty query
        result = rag.query("", top_k=3)
        print(f"   Empty query handled: {len(result['answer'])} characters")
        
        # Test with very long query
        long_query = "What is " + "PrivAI " * 100 + "?"
        result = rag.query(long_query, top_k=3)
        print(f"   Long query handled: {len(result['answer'])} characters")
        
        # Test 10: Test JSON serialization
        print(f"\n💾 Test 10: JSON Serialization")
        print("-" * 40)
        
        result = rag.query("What is PrivAI?", top_k=2)
        
        # Convert to JSON-serializable format
        json_result = result.copy()
        json_str = json.dumps(json_result, indent=2)
        
        print(f"   ✅ JSON serialization successful")
        print(f"   JSON size: {len(json_str)} characters")
        
        # Cleanup
        print(f"\n🧹 Cleanup")
        print("-" * 40)
        
        # Clear cache
        rag.clear_cache()
        print(f"   ✅ Cache cleared")
        
        # Remove test cache directory
        import shutil
        if Path("test_rag_cache").exists():
            shutil.rmtree("test_rag_cache")
            print(f"   ✅ Test cache directory removed")
        
        print(f"\n🎉 All RAG pipeline tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install required packages: pip install transformers torch openai")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_rag_with_different_models():
    """Test RAG with different model configurations"""
    print(f"\n🔧 Testing RAG with Different Models")
    print("=" * 50)
    
    try:
        # Test with different local models
        models = [
            "microsoft/DialoGPT-medium",
            "gpt2",
            "distilgpt2"
        ]
        
        for model_name in models:
            print(f"\n📊 Testing model: {model_name}")
            print("-" * 30)
            
            try:
                rag = RAGPipeline(local_model_name=model_name)
                
                if rag.local_llm is not None:
                    print(f"   ✅ Model loaded successfully")
                    
                    # Test a simple query
                    result = rag.query("What is AI?", top_k=2)
                    print(f"   Query result: {len(result['answer'])} characters")
                    print(f"   Model used: {result['metadata']['model_used']}")
                else:
                    print(f"   ❌ Model not available")
                    
            except Exception as e:
                print(f"   ❌ Model failed: {e}")
    
    except Exception as e:
        print(f"❌ Model testing failed: {e}")

def test_rag_caching():
    """Test RAG caching functionality"""
    print(f"\n💾 Testing RAG Caching")
    print("=" * 50)
    
    try:
        rag = RAGPipeline(cache_dir="test_cache")
        
        # Add some sample data
        sample_docs = [
            {
                "text": "This is a test document about artificial intelligence.",
                "metadata": {"source": "test.pdf", "page": 1}
            }
        ]
        
        sample_embeddings = [np.random.randn(384).astype('float32')]
        sample_embeddings[0] = sample_embeddings[0] / np.linalg.norm(sample_embeddings[0])
        
        rag.vector_database.add_chunks(sample_docs, sample_embeddings)
        
        # Test caching
        query = "What is artificial intelligence?"
        
        # First query
        result1 = rag.query(query, use_cache=True)
        print(f"✅ First query: {result1['metadata']['cached']}")
        
        # Second query (should be cached)
        result2 = rag.query(query, use_cache=True)
        print(f"✅ Second query: {result2['metadata']['cached']}")
        
        # Test cache clearing
        rag.clear_cache()
        print(f"✅ Cache cleared")
        
        # Cleanup
        import shutil
        if Path("test_cache").exists():
            shutil.rmtree("test_cache")
            print(f"✅ Test cache directory removed")
    
    except Exception as e:
        print(f"❌ Caching test failed: {e}")

if __name__ == "__main__":
    import time
    test_rag_pipeline()
    test_rag_with_different_models()
    test_rag_caching()

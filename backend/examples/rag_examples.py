"""
Examples demonstrating the PrivAI RAG functionality
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime

from app.core.rag import (
    RAGPipeline, 
    create_rag_pipeline, 
    query_rag, 
    get_default_rag_pipeline
)


def create_sample_knowledge_base():
    """Create a sample knowledge base for testing"""
    documents = [
        {
            "text": "PrivAI is a privacy-first AI application designed specifically for educational institutions. It provides secure, local processing of academic documents and data without sending any information to external servers, ensuring complete privacy and data protection.",
            "metadata": {
                "source_file": "privacy_policy.pdf",
                "page_number": 1,
                "chunk_index": 0,
                "chunk_type": "privacy_policy",
                "department": "IT",
                "confidentiality": "high",
                "last_updated": "2024-01-15"
            }
        },
        {
            "text": "The system uses advanced natural language processing techniques including transformer models and vector embeddings to understand and analyze document content. It can extract key information, answer complex questions, and provide intelligent insights based on the uploaded documents.",
            "metadata": {
                "source_file": "technical_specs.pdf",
                "page_number": 2,
                "chunk_index": 0,
                "chunk_type": "technical_document",
                "department": "Engineering",
                "confidentiality": "medium",
                "last_updated": "2024-01-20"
            }
        },
        {
            "text": "Students and faculty can upload various file types including PDFs, Word documents, Excel spreadsheets, and PowerPoint presentations. The system automatically processes these files, extracts text content, and creates searchable knowledge bases for easy information retrieval.",
            "metadata": {
                "source_file": "user_guide.pdf",
                "page_number": 3,
                "chunk_index": 0,
                "chunk_type": "user_guide",
                "department": "Academic",
                "confidentiality": "low",
                "last_updated": "2024-01-10"
            }
        },
        {
            "text": "Vector embeddings enable powerful semantic search capabilities. The system can find relevant information even when exact keywords don't match, using meaning and context to provide more accurate and comprehensive search results.",
            "metadata": {
                "source_file": "technical_specs.pdf",
                "page_number": 4,
                "chunk_index": 1,
                "chunk_type": "technical_document",
                "department": "Engineering",
                "confidentiality": "medium",
                "last_updated": "2024-01-20"
            }
        },
        {
            "text": "All data processing happens locally on the user's machine or institutional servers. This ensures complete privacy and security, as no sensitive academic information ever leaves the local environment, meeting strict data protection requirements.",
            "metadata": {
                "source_file": "privacy_policy.pdf",
                "page_number": 2,
                "chunk_index": 1,
                "chunk_type": "privacy_policy",
                "department": "IT",
                "confidentiality": "high",
                "last_updated": "2024-01-15"
            }
        },
        {
            "text": "The application supports multiple languages and can handle documents in various formats from different academic disciplines. It provides real-time processing and immediate results for user queries, making it an efficient tool for research and study.",
            "metadata": {
                "source_file": "user_guide.pdf",
                "page_number": 5,
                "chunk_index": 1,
                "chunk_type": "user_guide",
                "department": "Academic",
                "confidentiality": "low",
                "last_updated": "2024-01-10"
            }
        },
        {
            "text": "PrivAI integrates with existing learning management systems and can be deployed on-premises or in private clouds. It supports single sign-on authentication and role-based access control to ensure proper security and user management.",
            "metadata": {
                "source_file": "deployment_guide.pdf",
                "page_number": 1,
                "chunk_index": 0,
                "chunk_type": "deployment_guide",
                "department": "IT",
                "confidentiality": "medium",
                "last_updated": "2024-01-25"
            }
        },
        {
            "text": "The system provides detailed analytics and usage statistics to help institutions understand how the platform is being used. It tracks query patterns, popular documents, and user engagement to improve the overall experience.",
            "metadata": {
                "source_file": "analytics_guide.pdf",
                "page_number": 2,
                "chunk_index": 0,
                "chunk_type": "analytics_guide",
                "department": "Administration",
                "confidentiality": "low",
                "last_updated": "2024-01-30"
            }
        }
    ]
    
    return documents


def create_sample_embeddings(documents):
    """Create sample embeddings for documents"""
    embeddings = []
    
    for i, doc in enumerate(documents):
        # Create a deterministic embedding based on text content
        text = doc['text']
        hash_value = hash(text) % (2**32)
        np.random.seed(hash_value)
        
        # Generate random normalized embedding
        embedding = np.random.randn(384).astype('float32')
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add some semantic structure based on content
        if "privacy" in text.lower():
            embedding[0] += 0.5
        if "technical" in text.lower():
            embedding[1] += 0.5
        if "user" in text.lower():
            embedding[2] += 0.5
        if "deployment" in text.lower():
            embedding[3] += 0.5
        if "analytics" in text.lower():
            embedding[4] += 0.5
        
        # Renormalize
        embedding = embedding / np.linalg.norm(embedding)
        embeddings.append(embedding)
    
    return embeddings


def demonstrate_basic_rag():
    """Demonstrate basic RAG functionality"""
    print("🚀 PrivAI RAG Pipeline - Basic Demonstration")
    print("=" * 60)
    
    # Create sample knowledge base
    documents = create_sample_knowledge_base()
    embeddings = create_sample_embeddings(documents)
    
    print(f"✅ Created knowledge base with {len(documents)} documents")
    
    try:
        # Initialize RAG pipeline
        print(f"\n🔧 Initializing RAG Pipeline")
        print("-" * 40)
        
        rag = RAGPipeline(
            local_model_name="microsoft/DialoGPT-medium",
            cache_dir="demo_rag_cache"
        )
        
        print(f"✅ RAG pipeline initialized")
        print(f"   Local LLM available: {rag.local_llm is not None}")
        print(f"   OpenAI available: {rag.openai_client is not None}")
        print(f"   Cache directory: {rag.cache_dir}")
        
        # Add documents to vector database
        print(f"\n📚 Adding Documents to Knowledge Base")
        print("-" * 40)
        
        chunk_ids = rag.vector_database.add_chunks(documents, embeddings)
        
        print(f"✅ Added {len(chunk_ids)} documents to knowledge base")
        print(f"   Total chunks: {rag.vector_database.get_chunk_count()}")
        print(f"   Document types: {set(doc['metadata']['chunk_type'] for doc in documents)}")
        
        return rag
        
    except Exception as e:
        print(f"❌ Error in basic RAG setup: {e}")
        return None


def demonstrate_query_processing(rag):
    """Demonstrate query processing capabilities"""
    if not rag:
        return
    
    print(f"\n🔍 Query Processing Demonstration")
    print("-" * 40)
    
    # Test different types of queries
    queries = [
        {
            "query": "How does PrivAI ensure privacy?",
            "description": "Privacy-focused question"
        },
        {
            "query": "What file types are supported for upload?",
            "description": "Feature inquiry"
        },
        {
            "query": "How does the system process documents?",
            "description": "Technical process question"
        },
        {
            "query": "What are vector embeddings used for?",
            "description": "Technical concept question"
        },
        {
            "query": "Is data processing local or cloud-based?",
            "description": "Architecture question"
        },
        {
            "query": "How can institutions deploy PrivAI?",
            "description": "Deployment question"
        },
        {
            "query": "What analytics features are available?",
            "description": "Analytics question"
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        query = query_info["query"]
        description = query_info["description"]
        
        print(f"\n📝 Query {i}: {description}")
        print(f"   Question: '{query}'")
        
        try:
            # Process query
            result = rag.query(query, top_k=3, use_local_llm=True)
            
            print(f"   ✅ Answer: {result['answer'][:150]}...")
            print(f"   📊 Sources: {len(result['sources'])} documents")
            print(f"   ⏱️  Processing time: {result['metadata']['processing_time']:.2f}s")
            print(f"   🤖 Model used: {result['metadata']['model_used']}")
            
            # Show top sources
            print(f"   📚 Top sources:")
            for j, source in enumerate(result['sources'][:2]):
                similarity = source['similarity_score']
                source_file = source['metadata']['source_file']
                chunk_type = source['metadata']['chunk_type']
                text_preview = source['text'][:80] + "..." if len(source['text']) > 80 else source['text']
                
                print(f"     {j+1}. {source_file} ({chunk_type}) - Similarity: {similarity:.3f}")
                print(f"        {text_preview}")
        
        except Exception as e:
            print(f"   ❌ Query failed: {e}")


def demonstrate_advanced_queries(rag):
    """Demonstrate advanced query capabilities"""
    if not rag:
        return
    
    print(f"\n🚀 Advanced Query Demonstration")
    print("-" * 40)
    
    # Test different top-k values
    print(f"\n🔍 Testing Different Top-K Values")
    query = "What are the main features of PrivAI?"
    
    for top_k in [1, 3, 5, 8]:
        result = rag.query(query, top_k=top_k)
        print(f"   Top-K {top_k}: {len(result['sources'])} sources, "
              f"{result['metadata']['processing_time']:.2f}s")
    
    # Test query variations
    print(f"\n🔄 Testing Query Variations")
    base_query = "How does PrivAI work?"
    variations = [
        "How does PrivAI work?",
        "How does the PrivAI system work?",
        "Can you explain how PrivAI functions?",
        "What is the working mechanism of PrivAI?"
    ]
    
    for variation in variations:
        result = rag.query(variation, top_k=2)
        print(f"   '{variation[:30]}...': {len(result['sources'])} sources, "
              f"similarity: {result['sources'][0]['similarity_score']:.3f}")


def demonstrate_caching(rag):
    """Demonstrate caching functionality"""
    if not rag:
        return
    
    print(f"\n💾 Caching Demonstration")
    print("-" * 40)
    
    query = "What is PrivAI?"
    
    # First query (not cached)
    print(f"\n🔄 First Query (Not Cached)")
    start_time = time.time()
    result1 = rag.query(query, use_cache=True)
    first_time = time.time() - start_time
    
    print(f"   Processing time: {first_time:.2f}s")
    print(f"   Cached: {result1['metadata']['cached']}")
    print(f"   Answer length: {len(result1['answer'])} characters")
    
    # Second query (should be cached)
    print(f"\n🔄 Second Query (Cached)")
    start_time = time.time()
    result2 = rag.query(query, use_cache=True)
    second_time = time.time() - start_time
    
    print(f"   Processing time: {second_time:.2f}s")
    print(f"   Cached: {result2['metadata']['cached']}")
    print(f"   Answer length: {len(result2['answer'])} characters")
    
    # Compare results
    if result1['answer'] == result2['answer']:
        print(f"   ✅ Cached response matches original")
    else:
        print(f"   ⚠️  Cached response differs from original")
    
    if second_time < first_time * 0.5:  # Significant speedup
        print(f"   🚀 Caching provides {first_time/second_time:.1f}x speedup")
    else:
        print(f"   ⚠️  Caching may not be working optimally")
    
    # Test cache clearing
    print(f"\n🧹 Cache Management")
    rag.clear_cache()
    print(f"   ✅ Cache cleared")
    
    # Query after cache clear
    result3 = rag.query(query, use_cache=True)
    print(f"   Query after cache clear: {result3['metadata']['cached']}")


def demonstrate_prompt_construction(rag):
    """Demonstrate prompt construction"""
    if not rag:
        return
    
    print(f"\n📝 Prompt Construction Demonstration")
    print("-" * 40)
    
    query = "How does PrivAI ensure data privacy?"
    
    # Generate query embedding and retrieve chunks
    query_embedding = rag._generate_query_embedding(query)
    chunks = rag._retrieve_chunks(query_embedding, 3)
    
    # Construct prompt
    prompt = rag._construct_prompt(query, chunks)
    
    print(f"✅ Prompt constructed successfully")
    print(f"   Query: '{query}'")
    print(f"   Retrieved chunks: {len(chunks)}")
    print(f"   Prompt length: {len(prompt)} characters")
    
    # Show prompt structure
    print(f"\n📋 Prompt Structure:")
    print(f"   Template: {rag.prompt_template[:100]}...")
    print(f"   Retrieved chunks section: {len(prompt.split('--- Document')[1:])} documents")
    
    # Show sample prompt
    print(f"\n📄 Sample Prompt (first 500 characters):")
    print(f"   {prompt[:500]}...")


def demonstrate_model_comparison(rag):
    """Demonstrate different model configurations"""
    if not rag:
        return
    
    print(f"\n🤖 Model Comparison Demonstration")
    print("-" * 40)
    
    query = "What are the main benefits of PrivAI?"
    
    # Test with local LLM
    print(f"\n🔧 Local LLM Response")
    try:
        result_local = rag.query(query, top_k=3, use_local_llm=True)
        print(f"   Model: {result_local['metadata']['model_used']}")
        print(f"   Answer: {result_local['answer'][:100]}...")
        print(f"   Processing time: {result_local['metadata']['processing_time']:.2f}s")
    except Exception as e:
        print(f"   ❌ Local LLM failed: {e}")
    
    # Test with OpenAI (if available)
    print(f"\n🌐 OpenAI API Response")
    try:
        result_openai = rag.query(query, top_k=3, use_local_llm=False)
        print(f"   Model: {result_openai['metadata']['model_used']}")
        print(f"   Answer: {result_openai['answer'][:100]}...")
        print(f"   Processing time: {result_openai['metadata']['processing_time']:.2f}s")
    except Exception as e:
        print(f"   ❌ OpenAI API failed: {e}")


def demonstrate_convenience_functions(rag):
    """Demonstrate convenience functions"""
    if not rag:
        return
    
    print(f"\n🛠️  Convenience Functions Demonstration")
    print("-" * 40)
    
    # Test create_rag_pipeline
    print(f"\n📝 Testing create_rag_pipeline")
    rag2 = create_rag_pipeline()
    print(f"   ✅ Created RAG pipeline with convenience function")
    
    # Test query_rag
    print(f"\n🔍 Testing query_rag")
    result = query_rag("What is PrivAI?", top_k=2)
    print(f"   ✅ Query with convenience function: {len(result['sources'])} sources")
    
    # Test get_default_rag_pipeline
    print(f"\n🔧 Testing get_default_rag_pipeline")
    default_rag = get_default_rag_pipeline()
    print(f"   ✅ Got default RAG pipeline")


def demonstrate_error_handling(rag):
    """Demonstrate error handling capabilities"""
    if not rag:
        return
    
    print(f"\n⚠️  Error Handling Demonstration")
    print("-" * 40)
    
    # Test with empty query
    print(f"\n🔍 Empty Query Test")
    result = rag.query("", top_k=3)
    print(f"   Empty query handled: {len(result['answer'])} characters")
    
    # Test with very long query
    print(f"\n🔍 Long Query Test")
    long_query = "What is " + "PrivAI " * 50 + "?"
    result = rag.query(long_query, top_k=3)
    print(f"   Long query handled: {len(result['answer'])} characters")
    
    # Test with special characters
    print(f"\n🔍 Special Characters Test")
    special_query = "What is PrivAI? @#$%^&*()_+{}|:<>?[]\\;'\",./"
    result = rag.query(special_query, top_k=3)
    print(f"   Special characters handled: {len(result['answer'])} characters")


def demonstrate_statistics(rag):
    """Demonstrate RAG statistics"""
    if not rag:
        return
    
    print(f"\n📊 RAG Statistics Demonstration")
    print("-" * 40)
    
    stats = rag.get_stats()
    
    print(f"✅ RAG Pipeline Statistics:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"     {sub_key}: {sub_value}")
        else:
            print(f"   {key}: {value}")
    
    # Test cache statistics
    cache_files = list(rag.cache_dir.glob("*.json"))
    print(f"\n💾 Cache Statistics:")
    print(f"   Cached responses: {len(cache_files)}")
    print(f"   Cache directory: {rag.cache_dir}")


def main():
    """Run all demonstrations"""
    print("🎯 PrivAI RAG Pipeline - Complete Demonstration")
    print("=" * 70)
    
    # Basic RAG setup
    rag = demonstrate_basic_rag()
    
    if rag:
        # Query processing
        demonstrate_query_processing(rag)
        
        # Advanced queries
        demonstrate_advanced_queries(rag)
        
        # Caching
        demonstrate_caching(rag)
        
        # Prompt construction
        demonstrate_prompt_construction(rag)
        
        # Model comparison
        demonstrate_model_comparison(rag)
        
        # Convenience functions
        demonstrate_convenience_functions(rag)
        
        # Error handling
        demonstrate_error_handling(rag)
        
        # Statistics
        demonstrate_statistics(rag)
        
        # Cleanup
        print(f"\n🧹 Cleanup")
        print("-" * 40)
        
        rag.clear_cache()
        print(f"✅ Cache cleared")
        
        import shutil
        if Path("demo_rag_cache").exists():
            shutil.rmtree("demo_rag_cache")
            print(f"✅ Demo cache directory removed")
        
        print(f"\n🎉 All RAG demonstrations completed successfully!")
    else:
        print(f"\n❌ Could not complete demonstrations due to setup issues")


if __name__ == "__main__":
    import time
    main()

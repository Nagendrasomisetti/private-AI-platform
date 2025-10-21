"""
Examples demonstrating the PrivAI Embeddings functionality
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime

from app.core.embeddings import (
    EmbeddingGenerator, 
    generate_embeddings_for_chunks, 
    generate_query_embedding
)


def create_sample_documents():
    """Create sample documents for testing"""
    documents = [
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
        },
        {
            "text": "The application supports multiple languages and can handle documents in various formats. It provides real-time processing and immediate results for user queries.",
            "metadata": {
                "source_file": "user_guide.pdf",
                "page_number": 5,
                "chunk_index": 1,
                "chunk_type": "user_guide"
            }
        }
    ]
    
    return documents


def demonstrate_basic_embeddings():
    """Demonstrate basic embedding generation"""
    print("🚀 PrivAI Embeddings Demonstration")
    print("=" * 60)
    
    # Create sample documents
    documents = create_sample_documents()
    print(f"✅ Created {len(documents)} sample documents")
    
    try:
        # Initialize embedding generator
        print(f"\n🔧 Initializing Embedding Generator")
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
        
        # Generate embeddings
        print(f"\n📊 Generating Embeddings")
        print("-" * 40)
        
        documents_with_embeddings = generator.generate_embeddings(documents)
        
        print(f"✅ Generated embeddings for {len(documents_with_embeddings)} documents")
        
        # Show embedding details
        for i, doc in enumerate(documents_with_embeddings):
            embedding = doc.get('embedding')
            if embedding is not None:
                print(f"   Document {i+1}: {doc['text'][:60]}...")
                print(f"     Embedding shape: {embedding.shape}")
                print(f"     Embedding norm: {np.linalg.norm(embedding):.4f}")
                print(f"     Source: {doc['metadata']['source_file']}")
        
        return documents_with_embeddings, generator
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install sentence-transformers: pip install sentence-transformers")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None


def demonstrate_similarity_search(documents_with_embeddings, generator):
    """Demonstrate similarity search functionality"""
    if not documents_with_embeddings or not generator:
        return
    
    print(f"\n🔍 Similarity Search Demonstration")
    print("-" * 40)
    
    # Test queries
    queries = [
        "How does PrivAI ensure privacy?",
        "What file types are supported?",
        "How does the system process documents?",
        "What are vector embeddings used for?",
        "Is data processing local or cloud-based?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = generate_query_embedding(query)
            print(f"   Query embedding shape: {query_embedding.shape}")
            
            # Find similar documents
            similar_docs = generator.find_similar_chunks(
                query_embedding,
                documents_with_embeddings,
                top_k=3
            )
            
            print(f"   Top {len(similar_docs)} similar documents:")
            for j, doc in enumerate(similar_docs):
                similarity = doc['similarity_score']
                text = doc['text'][:80] + "..." if len(doc['text']) > 80 else doc['text']
                source = doc['metadata']['source_file']
                print(f"     {j+1}. Similarity: {similarity:.4f}")
                print(f"        Text: {text}")
                print(f"        Source: {source}")
        
        except Exception as e:
            print(f"   ❌ Error processing query: {e}")


def demonstrate_batch_processing(documents, generator):
    """Demonstrate batch processing capabilities"""
    if not generator:
        return
    
    print(f"\n⚡ Batch Processing Demonstration")
    print("-" * 40)
    
    # Test different batch sizes
    batch_sizes = [1, 2, 4, 8]
    
    for batch_size in batch_sizes:
        print(f"\n📦 Testing batch size: {batch_size}")
        
        try:
            start_time = datetime.now()
            
            # Process documents in batches
            documents_batch = generator.generate_embeddings(
                documents[:4],  # Use first 4 documents
                batch_size=batch_size,
                use_cache=False
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print(f"   ✅ Processed {len(documents_batch)} documents")
            print(f"   ⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"   📊 Documents per second: {len(documents_batch)/processing_time:.2f}")
            
        except Exception as e:
            print(f"   ❌ Error with batch size {batch_size}: {e}")


def demonstrate_caching(documents, generator):
    """Demonstrate embedding caching functionality"""
    if not generator:
        return
    
    print(f"\n💾 Caching Demonstration")
    print("-" * 40)
    
    # First run (no cache)
    print(f"\n🔄 First run (no cache)")
    start_time = datetime.now()
    documents_cached = generator.generate_embeddings(documents[:3], use_cache=True)
    first_run_time = (datetime.now() - start_time).total_seconds()
    print(f"   ✅ Processed {len(documents_cached)} documents in {first_run_time:.2f}s")
    
    # Second run (with cache)
    print(f"\n🔄 Second run (with cache)")
    start_time = datetime.now()
    documents_cached_2 = generator.generate_embeddings(documents[:3], use_cache=True)
    second_run_time = (datetime.now() - start_time).total_seconds()
    print(f"   ✅ Processed {len(documents_cached_2)} documents in {second_run_time:.2f}s")
    
    # Show speedup
    if first_run_time > 0:
        speedup = first_run_time / second_run_time if second_run_time > 0 else float('inf')
        print(f"   🚀 Speedup: {speedup:.2f}x faster")
    
    # Show cache statistics
    stats = generator.get_embedding_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Cached embeddings: {stats.get('cached_embeddings', 0)}")
    print(f"   Cache directory: {stats.get('cache_directory', 'N/A')}")


def demonstrate_embedding_quality(documents_with_embeddings, generator):
    """Demonstrate embedding quality analysis"""
    if not documents_with_embeddings or not generator:
        return
    
    print(f"\n🔬 Embedding Quality Analysis")
    print("-" * 40)
    
    # Analyze embedding properties
    embeddings = [doc['embedding'] for doc in documents_with_embeddings if 'embedding' in doc]
    
    if not embeddings:
        print("   ❌ No embeddings found for analysis")
        return
    
    embeddings_array = np.array(embeddings)
    
    # Calculate statistics
    norms = np.linalg.norm(embeddings_array, axis=1)
    mean_norm = np.mean(norms)
    std_norm = np.std(norms)
    
    print(f"   📊 Embedding Statistics:")
    print(f"     Mean norm: {mean_norm:.4f}")
    print(f"     Std norm: {std_norm:.4f}")
    print(f"     Min norm: {np.min(norms):.4f}")
    print(f"     Max norm: {np.max(norms):.4f}")
    
    # Check normalization (should be close to 1.0 for normalized embeddings)
    print(f"   🔍 Normalization Check:")
    print(f"     All embeddings normalized: {np.allclose(norms, 1.0, atol=1e-6)}")
    
    # Calculate pairwise similarities
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            sim = generator.compute_similarity(embeddings[i], embeddings[j])
            similarities.append(sim)
    
    if similarities:
        similarities = np.array(similarities)
        print(f"   📈 Similarity Statistics:")
        print(f"     Mean similarity: {np.mean(similarities):.4f}")
        print(f"     Std similarity: {np.std(similarities):.4f}")
        print(f"     Min similarity: {np.min(similarities):.4f}")
        print(f"     Max similarity: {np.max(similarities):.4f}")


def demonstrate_convenience_functions(documents):
    """Demonstrate convenience functions"""
    print(f"\n🛠️  Convenience Functions Demonstration")
    print("-" * 40)
    
    try:
        # Test generate_embeddings_for_chunks
        print(f"\n📝 Testing generate_embeddings_for_chunks")
        convenience_chunks = generate_embeddings_for_chunks(documents[:2])
        print(f"   ✅ Generated {len(convenience_chunks)} embeddings")
        
        # Test generate_query_embedding
        print(f"\n❓ Testing generate_query_embedding")
        query = "What is PrivAI?"
        query_embedding = generate_query_embedding(query)
        print(f"   ✅ Generated query embedding for: '{query}'")
        print(f"   📊 Embedding shape: {query_embedding.shape}")
        
    except Exception as e:
        print(f"   ❌ Error testing convenience functions: {e}")


def demonstrate_json_serialization(documents_with_embeddings):
    """Demonstrate JSON serialization for API responses"""
    if not documents_with_embeddings:
        return
    
    print(f"\n💾 JSON Serialization Demonstration")
    print("-" * 40)
    
    try:
        # Convert numpy arrays to lists for JSON serialization
        json_ready_docs = []
        for doc in documents_with_embeddings[:2]:  # Use first 2 documents
            json_doc = doc.copy()
            if 'embedding' in json_doc:
                json_doc['embedding'] = json_doc['embedding'].tolist()
            json_ready_docs.append(json_doc)
        
        # Serialize to JSON
        json_str = json.dumps(json_ready_docs, indent=2)
        print(f"   ✅ JSON serialization successful")
        print(f"   📊 JSON size: {len(json_str)} characters")
        print(f"   📄 Sample JSON (first 200 chars):")
        print(f"     {json_str[:200]}...")
        
        # Test deserialization
        deserialized_docs = json.loads(json_str)
        print(f"   ✅ JSON deserialization successful")
        print(f"   📊 Deserialized {len(deserialized_docs)} documents")
        
    except Exception as e:
        print(f"   ❌ JSON serialization error: {e}")


def main():
    """Run all demonstrations"""
    print("🎯 PrivAI Embeddings Module - Complete Demonstration")
    print("=" * 70)
    
    # Basic embeddings
    documents_with_embeddings, generator = demonstrate_basic_embeddings()
    
    if documents_with_embeddings and generator:
        # Similarity search
        demonstrate_similarity_search(documents_with_embeddings, generator)
        
        # Batch processing
        documents = create_sample_documents()
        demonstrate_batch_processing(documents, generator)
        
        # Caching
        demonstrate_caching(documents, generator)
        
        # Quality analysis
        demonstrate_embedding_quality(documents_with_embeddings, generator)
        
        # Convenience functions
        demonstrate_convenience_functions(documents)
        
        # JSON serialization
        demonstrate_json_serialization(documents_with_embeddings)
        
        print(f"\n🎉 All demonstrations completed successfully!")
    else:
        print(f"\n❌ Could not complete demonstrations due to missing dependencies")


if __name__ == "__main__":
    main()

"""
Examples demonstrating the PrivAI Vector Database functionality
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime

from app.core.vector_db import (
    VectorDatabase, 
    create_vector_database, 
    load_vector_database,
    get_default_vector_database
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
                "chunk_type": "privacy_policy",
                "department": "IT",
                "confidentiality": "high"
            }
        },
        {
            "text": "The system uses advanced natural language processing techniques to understand and analyze document content. It can extract key information, answer questions, and provide intelligent insights.",
            "metadata": {
                "source_file": "technical_specs.pdf",
                "page_number": 2,
                "chunk_index": 0,
                "chunk_type": "technical_document",
                "department": "Engineering",
                "confidentiality": "medium"
            }
        },
        {
            "text": "Students can upload various file types including PDFs, Word documents, and spreadsheets. The system automatically processes these files and creates searchable knowledge bases.",
            "metadata": {
                "source_file": "user_guide.pdf",
                "page_number": 3,
                "chunk_index": 0,
                "chunk_type": "user_guide",
                "department": "Academic",
                "confidentiality": "low"
            }
        },
        {
            "text": "Vector embeddings enable semantic search capabilities. The system can find relevant information even when exact keywords don't match, using meaning and context.",
            "metadata": {
                "source_file": "technical_specs.pdf",
                "page_number": 4,
                "chunk_index": 1,
                "chunk_type": "technical_document",
                "department": "Engineering",
                "confidentiality": "medium"
            }
        },
        {
            "text": "All data processing happens locally on the user's machine. This ensures complete privacy and security, as no sensitive information ever leaves the local environment.",
            "metadata": {
                "source_file": "privacy_policy.pdf",
                "page_number": 2,
                "chunk_index": 1,
                "chunk_type": "privacy_policy",
                "department": "IT",
                "confidentiality": "high"
            }
        },
        {
            "text": "The application supports multiple languages and can handle documents in various formats. It provides real-time processing and immediate results for user queries.",
            "metadata": {
                "source_file": "user_guide.pdf",
                "page_number": 5,
                "chunk_index": 1,
                "chunk_type": "user_guide",
                "department": "Academic",
                "confidentiality": "low"
            }
        }
    ]
    
    return documents


def create_sample_embeddings(documents):
    """Create sample embeddings for documents"""
    embeddings = []
    
    for i, doc in enumerate(documents):
        # Create a deterministic embedding based on text content
        # In real usage, these would come from the embeddings module
        text = doc['text']
        
        # Create a simple hash-based embedding for demonstration
        hash_value = hash(text) % (2**32)
        np.random.seed(hash_value)
        
        # Generate random normalized embedding
        embedding = np.random.randn(384).astype('float32')
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add some semantic structure based on content
        if "privacy" in text.lower():
            embedding[0] += 0.5  # Privacy-related content
        if "technical" in text.lower():
            embedding[1] += 0.5  # Technical content
        if "user" in text.lower():
            embedding[2] += 0.5  # User-related content
        
        # Renormalize
        embedding = embedding / np.linalg.norm(embedding)
        embeddings.append(embedding)
    
    return embeddings


def demonstrate_basic_operations():
    """Demonstrate basic vector database operations"""
    print("🚀 PrivAI Vector Database - Basic Operations")
    print("=" * 60)
    
    # Create sample data
    documents = create_sample_documents()
    embeddings = create_sample_embeddings(documents)
    
    print(f"✅ Created {len(documents)} sample documents with embeddings")
    
    try:
        # Initialize vector database
        print(f"\n🔧 Initializing Vector Database")
        print("-" * 40)
        
        db = VectorDatabase(
            embedding_dim=384,
            index_type="flat",
            metric="cosine"
        )
        
        print(f"✅ Database initialized")
        print(f"   Embedding dimension: {db.embedding_dim}")
        print(f"   Index type: {db.index_type}")
        print(f"   Metric: {db.metric}")
        
        # Add documents to database
        print(f"\n📝 Adding Documents to Database")
        print("-" * 40)
        
        chunk_ids = db.add_chunks(documents, embeddings)
        
        print(f"✅ Added {len(chunk_ids)} documents to database")
        print(f"   Chunk IDs: {[id[:8] + '...' for id in chunk_ids[:3]]}")
        print(f"   Total chunks: {db.get_chunk_count()}")
        print(f"   Metadata entries: {db.get_metadata_count()}")
        
        return db, chunk_ids
        
    except Exception as e:
        print(f"❌ Error in basic operations: {e}")
        return None, None


def demonstrate_querying(db, chunk_ids):
    """Demonstrate querying capabilities"""
    if not db or not chunk_ids:
        return
    
    print(f"\n🔍 Querying Demonstration")
    print("-" * 40)
    
    # Test queries
    queries = [
        "How does PrivAI ensure privacy?",
        "What file types are supported?",
        "How does the system process documents?",
        "What are vector embeddings used for?",
        "Is data processing local or cloud-based?"
    ]
    
    for i, query_text in enumerate(queries, 1):
        print(f"\n📝 Query {i}: '{query_text}'")
        
        try:
            # Create query embedding (simplified for demo)
            query_embedding = create_sample_embeddings([{"text": query_text}])[0]
            
            # Query the database
            results = db.query_top_k(query_embedding, k=3)
            
            print(f"   ✅ Found {len(results)} results:")
            for j, result in enumerate(results):
                similarity = result['similarity_score']
                text = result['text'][:80] + "..." if len(result['text']) > 80 else result['text']
                source = result['metadata']['source_file']
                chunk_type = result['metadata']['chunk_type']
                
                print(f"     {j+1}. Similarity: {similarity:.4f}")
                print(f"        Text: {text}")
                print(f"        Source: {source} ({chunk_type})")
        
        except Exception as e:
            print(f"   ❌ Query failed: {e}")


def demonstrate_metadata_filtering(db, chunk_ids):
    """Demonstrate metadata filtering capabilities"""
    if not db or not chunk_ids:
        return
    
    print(f"\n🔍 Metadata Filtering Demonstration")
    print("-" * 40)
    
    # Create a query embedding
    query_text = "How does the system work?"
    query_embedding = create_sample_embeddings([{"text": query_text}])[0]
    
    # Test different filters
    filters = [
        {"chunk_type": "privacy_policy"},
        {"chunk_type": "technical_document"},
        {"chunk_type": "user_guide"},
        {"department": "IT"},
        {"department": "Engineering"},
        {"confidentiality": "high"},
        {"confidentiality": "low"}
    ]
    
    for filter_dict in filters:
        print(f"\n🔍 Filter: {filter_dict}")
        
        try:
            results = db.search_by_metadata(filter_dict, query_embedding, k=2)
            
            print(f"   ✅ Found {len(results)} filtered results:")
            for result in results:
                similarity = result['similarity_score']
                text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
                metadata = result['metadata']
                
                print(f"     - Similarity: {similarity:.4f}")
                print(f"       Text: {text}")
                print(f"       Type: {metadata['chunk_type']}, Dept: {metadata['department']}")
        
        except Exception as e:
            print(f"   ❌ Filter failed: {e}")


def demonstrate_persistence(db, chunk_ids):
    """Demonstrate save/load functionality"""
    if not db or not chunk_ids:
        return
    
    print(f"\n💾 Persistence Demonstration")
    print("-" * 40)
    
    try:
        # Save the database
        save_path = "demo_vector_index"
        db.save_index(save_path)
        print(f"✅ Database saved to: {save_path}")
        
        # Create a new database and load the saved one
        print(f"\n📂 Loading saved database")
        db2 = VectorDatabase(embedding_dim=384, index_path=save_path)
        loaded = db2.load_index()
        
        if loaded:
            print(f"✅ Database loaded successfully")
            print(f"   Loaded chunks: {db2.get_chunk_count()}")
            print(f"   Loaded metadata: {db2.get_metadata_count()}")
            
            # Test query on loaded database
            query_text = "What is PrivAI?"
            query_embedding = create_sample_embeddings([{"text": query_text}])[0]
            results = db2.query_top_k(query_embedding, k=2)
            
            print(f"   Query on loaded DB: {len(results)} results")
            for result in results:
                print(f"     - {result['text'][:50]}... (similarity: {result['similarity_score']:.4f})")
        else:
            print(f"❌ Failed to load database")
        
        # Cleanup
        import shutil
        if Path(save_path).exists():
            shutil.rmtree(save_path)
            print(f"✅ Cleaned up test directory")
    
    except Exception as e:
        print(f"❌ Persistence demonstration failed: {e}")


def demonstrate_different_index_types():
    """Demonstrate different FAISS index types"""
    print(f"\n🔧 Different Index Types Demonstration")
    print("-" * 60)
    
    documents = create_sample_documents()[:3]  # Use first 3 documents
    embeddings = create_sample_embeddings(documents)
    
    index_types = [
        ("flat", "Flat index - exact search, good for small datasets"),
        ("ivf", "IVF index - approximate search, good for large datasets"),
        ("hnsw", "HNSW index - approximate search, good for very large datasets")
    ]
    
    for index_type, description in index_types:
        print(f"\n📊 Testing {index_type.upper()} Index")
        print(f"   {description}")
        print("-" * 50)
        
        try:
            # Create database with specific index type
            db = VectorDatabase(
                embedding_dim=384,
                index_type=index_type,
                metric="cosine"
            )
            
            # Add documents
            chunk_ids = db.add_chunks(documents, embeddings)
            print(f"   ✅ Added {len(chunk_ids)} documents")
            
            # Test query
            query_embedding = embeddings[0]  # Use first document as query
            results = db.query_top_k(query_embedding, k=2)
            
            print(f"   ✅ Query successful: {len(results)} results")
            if results:
                print(f"   📊 Top result similarity: {results[0]['similarity_score']:.4f}")
            
            # Show statistics
            stats = db.get_stats()
            print(f"   📈 Index trained: {stats.get('is_trained', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ {index_type} index failed: {e}")


def demonstrate_convenience_functions():
    """Demonstrate convenience functions"""
    print(f"\n🛠️  Convenience Functions Demonstration")
    print("-" * 60)
    
    try:
        # Test create_vector_database
        print(f"\n📝 Testing create_vector_database")
        db1 = create_vector_database(
            embedding_dim=384,
            index_type="flat",
            index_path="test_convenience"
        )
        
        print(f"✅ Created database with convenience function")
        print(f"   Embedding dim: {db1.embedding_dim}")
        print(f"   Index type: {db1.index_type}")
        
        # Test with sample data
        documents = create_sample_documents()[:2]
        embeddings = create_sample_embeddings(documents)
        
        chunk_ids = db1.add_chunks(documents, embeddings)
        print(f"✅ Added {len(chunk_ids)} documents")
        
        # Test get_default_vector_database
        print(f"\n🔧 Testing get_default_vector_database")
        default_db = get_default_vector_database()
        print(f"✅ Got default database")
        print(f"   Embedding dim: {default_db.embedding_dim}")
        print(f"   Index type: {default_db.index_type}")
        
        # Cleanup
        import shutil
        if Path("test_convenience").exists():
            shutil.rmtree("test_convenience")
            print(f"✅ Cleaned up test directory")
    
    except Exception as e:
        print(f"❌ Convenience functions demonstration failed: {e}")


def demonstrate_advanced_features(db, chunk_ids):
    """Demonstrate advanced features"""
    if not db or not chunk_ids:
        return
    
    print(f"\n🚀 Advanced Features Demonstration")
    print("-" * 40)
    
    try:
        # Test chunk retrieval by ID
        print(f"\n🔎 Chunk Retrieval by ID")
        if chunk_ids:
            chunk_id = chunk_ids[0]
            chunk_data = db.get_chunk_by_id(chunk_id)
            
            if chunk_data:
                print(f"✅ Retrieved chunk: {chunk_id[:8]}...")
                print(f"   Text: {chunk_data['text'][:60]}...")
                print(f"   Metadata: {chunk_data['metadata']}")
            else:
                print(f"❌ Failed to retrieve chunk")
        
        # Test database statistics
        print(f"\n📊 Database Statistics")
        stats = db.get_stats()
        print(f"✅ Database statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test chunk existence
        print(f"\n✅ Chunk Existence Check")
        if chunk_ids:
            exists = chunk_ids[0] in db
            print(f"   First chunk exists: {exists}")
            
            fake_id = "fake-chunk-id"
            exists_fake = fake_id in db
            print(f"   Fake chunk exists: {exists_fake}")
        
        # Test database length
        print(f"\n📏 Database Length")
        print(f"   Total chunks: {len(db)}")
        print(f"   Chunk count method: {db.get_chunk_count()}")
        
        # Test JSON serialization of results
        print(f"\n💾 JSON Serialization")
        query_embedding = create_sample_embeddings([{"text": "test query"}])[0]
        results = db.query_top_k(query_embedding, k=2)
        
        json_results = []
        for result in results:
            json_result = result.copy()
            json_results.append(json_result)
        
        json_str = json.dumps(json_results, indent=2)
        print(f"✅ JSON serialization successful")
        print(f"   JSON size: {len(json_str)} characters")
        print(f"   Sample JSON: {json_str[:200]}...")
    
    except Exception as e:
        print(f"❌ Advanced features demonstration failed: {e}")


def main():
    """Run all demonstrations"""
    print("🎯 PrivAI Vector Database - Complete Demonstration")
    print("=" * 70)
    
    # Basic operations
    db, chunk_ids = demonstrate_basic_operations()
    
    if db and chunk_ids:
        # Querying
        demonstrate_querying(db, chunk_ids)
        
        # Metadata filtering
        demonstrate_metadata_filtering(db, chunk_ids)
        
        # Persistence
        demonstrate_persistence(db, chunk_ids)
        
        # Advanced features
        demonstrate_advanced_features(db, chunk_ids)
    
    # Different index types
    demonstrate_different_index_types()
    
    # Convenience functions
    demonstrate_convenience_functions()
    
    print(f"\n🎉 All demonstrations completed successfully!")


if __name__ == "__main__":
    main()

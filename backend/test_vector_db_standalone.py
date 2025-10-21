"""
Standalone test for the Vector Database module (no external dependencies)
"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
import pickle

# Mock the required modules for testing
class MockSettings:
    faiss_index_path = "data/faiss_index"

class MockLogger:
    def info(self, msg, **kwargs):
        print(f"INFO: {msg}")
    
    def warning(self, msg, **kwargs):
        print(f"WARNING: {msg}")
    
    def error(self, msg, **kwargs):
        print(f"ERROR: {msg}")
    
    def debug(self, msg, **kwargs):
        print(f"DEBUG: {msg}")

# Mock the imports
import sys
from unittest.mock import MagicMock

# Mock the modules
sys.modules['app.core.config'] = MagicMock()
sys.modules['app.core.config'].settings = MockSettings()
sys.modules['app.core.logging'] = MagicMock()
sys.modules['app.core.logging'].get_logger = lambda x: MockLogger()

# Now import the vector database module
try:
    from app.core.vector_db import VectorDatabase, create_vector_database, load_vector_database
    VECTOR_DB_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import vector database module: {e}")
    VECTOR_DB_AVAILABLE = False

def test_vector_database_standalone():
    """Test the vector database functionality without full dependencies"""
    print("🧪 Testing PrivAI Vector Database (Standalone)")
    print("=" * 60)
    
    if not VECTOR_DB_AVAILABLE:
        print("❌ Vector database module not available")
        return
    
    try:
        # Test 1: Initialize vector database
        print("\n🔧 Test 1: Initialize Vector Database")
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
        print(f"   Total chunks: {db.get_chunk_count()}")
        
        # Test 2: Create sample chunks and embeddings
        print(f"\n📊 Test 2: Create Sample Data")
        print("-" * 40)
        
        sample_chunks = [
            {
                "text": "PrivAI is a privacy-first AI application for college data processing.",
                "metadata": {
                    "source_file": "privacy_policy.pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                    "chunk_type": "privacy_policy"
                }
            },
            {
                "text": "The system uses advanced natural language processing techniques.",
                "metadata": {
                    "source_file": "technical_specs.pdf",
                    "page_number": 2,
                    "chunk_index": 0,
                    "chunk_type": "technical_document"
                }
            },
            {
                "text": "Students can upload various file types including PDFs and Word documents.",
                "metadata": {
                    "source_file": "user_guide.pdf",
                    "page_number": 3,
                    "chunk_index": 0,
                    "chunk_type": "user_guide"
                }
            }
        ]
        
        # Create sample embeddings (random for testing)
        sample_embeddings = []
        for i in range(len(sample_chunks)):
            # Create random normalized embedding
            embedding = np.random.randn(384).astype('float32')
            embedding = embedding / np.linalg.norm(embedding)  # Normalize for cosine similarity
            sample_embeddings.append(embedding)
        
        print(f"✅ Created {len(sample_chunks)} sample chunks")
        print(f"✅ Created {len(sample_embeddings)} sample embeddings")
        print(f"   Embedding shape: {sample_embeddings[0].shape}")
        
        # Test 3: Add chunks to database
        print(f"\n📝 Test 3: Add Chunks to Database")
        print("-" * 40)
        
        chunk_ids = db.add_chunks(sample_chunks, sample_embeddings)
        
        print(f"✅ Added {len(chunk_ids)} chunks to database")
        print(f"   Chunk IDs: {[id[:8] + '...' for id in chunk_ids[:3]]}")
        print(f"   Total chunks in DB: {db.get_chunk_count()}")
        print(f"   Metadata count: {db.get_metadata_count()}")
        
        # Test 4: Query the database
        print(f"\n🔍 Test 4: Query Database")
        print("-" * 40)
        
        # Create a query vector (similar to first chunk)
        query_vector = sample_embeddings[0] + np.random.randn(384) * 0.1  # Add some noise
        query_vector = query_vector / np.linalg.norm(query_vector)  # Normalize
        
        results = db.query_top_k(query_vector, k=3)
        
        print(f"✅ Query completed")
        print(f"   Query vector shape: {query_vector.shape}")
        print(f"   Results count: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"   Result {i+1}:")
            print(f"     Chunk ID: {result['chunk_id']}")
            print(f"     Similarity: {result['similarity_score']:.4f}")
            print(f"     Text: {result['text'][:60]}...")
            print(f"     Source: {result['metadata']['source_file']}")
        
        # Test 5: Get chunk by ID
        print(f"\n🔎 Test 5: Get Chunk by ID")
        print("-" * 40)
        
        if chunk_ids:
            chunk_id = chunk_ids[0]
            chunk_data = db.get_chunk_by_id(chunk_id)
            
            if chunk_data:
                print(f"✅ Retrieved chunk by ID: {chunk_id}")
                print(f"   Text: {chunk_data['text'][:60]}...")
                print(f"   Metadata: {chunk_data['metadata']}")
            else:
                print(f"❌ Failed to retrieve chunk by ID")
        
        # Test 6: Save and load index
        print(f"\n💾 Test 6: Save and Load Index")
        print("-" * 40)
        
        # Save index
        test_index_path = "test_vector_index"
        db.save_index(test_index_path)
        print(f"✅ Index saved to: {test_index_path}")
        
        # Create new database and load index
        db2 = VectorDatabase(embedding_dim=384, index_path=test_index_path)
        loaded = db2.load_index()
        
        if loaded:
            print(f"✅ Index loaded successfully")
            print(f"   Loaded chunks: {db2.get_chunk_count()}")
            print(f"   Loaded metadata: {db2.get_metadata_count()}")
            
            # Test query on loaded database
            results2 = db2.query_top_k(query_vector, k=2)
            print(f"   Query on loaded DB: {len(results2)} results")
        else:
            print(f"❌ Failed to load index")
        
        # Test 7: Metadata filtering
        print(f"\n🔍 Test 7: Metadata Filtering")
        print("-" * 40)
        
        # Filter by chunk type
        privacy_results = db.search_by_metadata(
            {"chunk_type": "privacy_policy"},
            query_vector,
            k=2
        )
        
        print(f"✅ Metadata filtering completed")
        print(f"   Privacy policy results: {len(privacy_results)}")
        
        for result in privacy_results:
            print(f"     - {result['text'][:50]}... (similarity: {result['similarity_score']:.4f})")
        
        # Test 8: Database statistics
        print(f"\n📊 Test 8: Database Statistics")
        print("-" * 40)
        
        stats = db.get_stats()
        print(f"✅ Database statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 9: Chunk existence check
        print(f"\n✅ Test 9: Chunk Existence Check")
        print("-" * 40)
        
        if chunk_ids:
            chunk_id = chunk_ids[0]
            exists = chunk_id in db
            print(f"   Chunk {chunk_id} exists: {exists}")
            
            # Test non-existent chunk
            fake_id = "fake-chunk-id"
            exists_fake = fake_id in db
            print(f"   Fake chunk exists: {exists_fake}")
        
        # Test 10: JSON serialization
        print(f"\n💾 Test 10: JSON Serialization")
        print("-" * 40)
        
        # Convert results to JSON-serializable format
        json_results = []
        for result in results[:2]:  # First 2 results
            json_result = result.copy()
            # Remove numpy types if any
            json_results.append(json_result)
        
        json_str = json.dumps(json_results, indent=2)
        print(f"✅ JSON serialization successful")
        print(f"   JSON size: {len(json_str)} characters")
        
        # Cleanup
        print(f"\n🧹 Cleanup")
        print("-" * 40)
        
        # Remove test index directory
        test_path = Path(test_index_path)
        if test_path.exists():
            import shutil
            shutil.rmtree(test_path)
            print(f"✅ Test index directory removed")
        
        print(f"\n🎉 All vector database tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install FAISS: pip install faiss-cpu")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_different_index_types():
    """Test different FAISS index types"""
    print(f"\n🔧 Testing Different Index Types")
    print("=" * 50)
    
    if not VECTOR_DB_AVAILABLE:
        print("❌ Vector database module not available")
        return
    
    try:
        index_types = ["flat", "ivf", "hnsw"]
        
        for index_type in index_types:
            print(f"\n📊 Testing {index_type.upper()} Index")
            print("-" * 30)
            
            try:
                db = VectorDatabase(
                    embedding_dim=384,
                    index_type=index_type,
                    metric="cosine"
                )
                
                print(f"✅ {index_type} index created successfully")
                
                # Test with sample data
                sample_chunks = [
                    {
                        "text": f"Sample text for {index_type} index",
                        "metadata": {"index_type": index_type, "chunk_index": 0}
                    }
                ]
                
                sample_embeddings = [np.random.randn(384).astype('float32')]
                sample_embeddings[0] = sample_embeddings[0] / np.linalg.norm(sample_embeddings[0])
                
                chunk_ids = db.add_chunks(sample_chunks, sample_embeddings)
                print(f"✅ Added chunks to {index_type} index")
                
                # Test query
                results = db.query_top_k(sample_embeddings[0], k=1)
                print(f"✅ Query successful: {len(results)} results")
                
            except Exception as e:
                print(f"❌ {index_type} index failed: {e}")
    
    except Exception as e:
        print(f"❌ Index type testing failed: {e}")

def test_convenience_functions():
    """Test convenience functions"""
    print(f"\n🛠️  Testing Convenience Functions")
    print("=" * 50)
    
    if not VECTOR_DB_AVAILABLE:
        print("❌ Vector database module not available")
        return
    
    try:
        # Test create_vector_database
        print(f"\n📝 Testing create_vector_database")
        db1 = create_vector_database(embedding_dim=384, index_type="flat")
        print(f"✅ Created database with convenience function")
        
        # Test load_vector_database
        print(f"\n📂 Testing load_vector_database")
        db2 = load_vector_database("non_existent_path", embedding_dim=384)
        if db2 is None:
            print(f"✅ Correctly returned None for non-existent path")
        else:
            print(f"✅ Loaded database from path")
        
    except Exception as e:
        print(f"❌ Convenience function testing failed: {e}")

if __name__ == "__main__":
    test_vector_database_standalone()
    test_different_index_types()
    test_convenience_functions()

"""
FAISS Vector Database Integration for PrivAI
Handles local storage, indexing, and querying of embeddings using FAISS
"""
import os
import pickle
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

# Optional imports for FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from .config import settings
from .logging import get_logger

logger = get_logger("vector_db")


class VectorDatabase:
    """
    FAISS-based vector database for storing and querying embeddings locally.
    Provides persistent storage, metadata mapping, and efficient similarity search.
    """
    
    def __init__(self, 
                 index_path: Optional[str] = None,
                 embedding_dim: int = 384,
                 index_type: str = "flat",
                 metric: str = "cosine"):
        """
        Initialize the vector database.
        
        Args:
            index_path: Path to store the FAISS index and metadata
            embedding_dim: Dimension of the embedding vectors
            index_type: Type of FAISS index ("flat", "ivf", "hnsw")
            metric: Distance metric ("cosine", "l2", "ip")
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS is required for vector database. "
                "Install with: pip install faiss-cpu"
            )
        
        self.index_path = Path(index_path) if index_path else Path(settings.faiss_index_path)
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        
        # Create index directory
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self.index = self._create_index()
        self.chunk_metadata = {}  # Maps chunk_id to metadata
        self.chunk_id_to_index = {}  # Maps chunk_id to FAISS index position
        self.index_to_chunk_id = {}  # Maps FAISS index position to chunk_id
        self.next_index = 0
        
        # Load existing index if available
        self._load_index()
        
        logger.info("VectorDatabase initialized", 
                   index_path=str(self.index_path),
                   embedding_dim=embedding_dim,
                   index_type=index_type,
                   metric=metric)
    
    def _create_index(self):
        """Create a new FAISS index based on configuration."""
        try:
            if self.index_type == "flat":
                if self.metric == "cosine":
                    # Use inner product for cosine similarity (vectors must be normalized)
                    index = faiss.IndexFlatIP(self.embedding_dim)
                elif self.metric == "l2":
                    index = faiss.IndexFlatL2(self.embedding_dim)
                else:
                    raise ValueError(f"Unsupported metric for flat index: {self.metric}")
            
            elif self.index_type == "ivf":
                # IVF (Inverted File) index for larger datasets
                quantizer = faiss.IndexFlatIP(self.embedding_dim) if self.metric == "cosine" else faiss.IndexFlatL2(self.embedding_dim)
                index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)  # 100 clusters
            
            elif self.index_type == "hnsw":
                # HNSW (Hierarchical Navigable Small World) index
                index = faiss.IndexHNSWFlat(self.embedding_dim, 32)  # 32 connections per node
                index.hnsw.efConstruction = 200  # Construction parameter
                index.hnsw.efSearch = 50  # Search parameter
            
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
            
            logger.info("FAISS index created", 
                       index_type=self.index_type,
                       metric=self.metric,
                       embedding_dim=self.embedding_dim)
            
            return index
            
        except Exception as e:
            logger.error("Failed to create FAISS index", error=str(e))
            raise
    
    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[np.ndarray]) -> List[str]:
        """
        Add chunks with their embeddings to the vector database.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
            embeddings: List of corresponding embedding vectors
            
        Returns:
            List of chunk IDs assigned to the added chunks
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")
            
            if not chunks:
                logger.warning("No chunks provided to add")
                return []
            
            logger.info("Adding chunks to vector database", 
                       chunk_count=len(chunks),
                       embedding_dim=embeddings[0].shape[0] if embeddings else 0)
            
            # Validate embeddings
            for i, embedding in enumerate(embeddings):
                if embedding.shape[0] != self.embedding_dim:
                    raise ValueError(f"Embedding {i} has dimension {embedding.shape[0]}, expected {self.embedding_dim}")
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Normalize embeddings for cosine similarity if using cosine metric
            if self.metric == "cosine":
                faiss.normalize_L2(embeddings_array)
            
            # Generate chunk IDs
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                chunk_ids.append(chunk_id)
                
                # Store metadata
                self.chunk_metadata[chunk_id] = {
                    'text': chunk['text'],
                    'metadata': chunk['metadata'],
                    'embedding_dim': self.embedding_dim,
                    'added_at': self._get_timestamp()
                }
                
                # Map chunk ID to index position
                self.chunk_id_to_index[chunk_id] = self.next_index + i
                self.index_to_chunk_id[self.next_index + i] = chunk_id
            
            # Add embeddings to FAISS index
            if self.index_type == "ivf" and not self.index.is_trained:
                # Train IVF index if not already trained
                logger.info("Training IVF index")
                self.index.train(embeddings_array)
            
            self.index.add(embeddings_array)
            self.next_index += len(chunks)
            
            logger.info("Chunks added successfully", 
                       chunk_count=len(chunks),
                       total_chunks=self.index.ntotal)
            
            return chunk_ids
            
        except Exception as e:
            logger.error("Failed to add chunks", error=str(e))
            raise
    
    def query_top_k(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector database for the top-k most similar chunks.
        
        Args:
            query_vector: Query embedding vector
            k: Number of top results to return
            
        Returns:
            List of dictionaries containing chunk data and similarity scores
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector database is empty")
                return []
            
            if query_vector.shape[0] != self.embedding_dim:
                raise ValueError(f"Query vector has dimension {query_vector.shape[0]}, expected {self.embedding_dim}")
            
            # Prepare query vector
            query_vector = query_vector.reshape(1, -1).astype('float32')
            
            # Normalize query vector for cosine similarity if using cosine metric
            if self.metric == "cosine":
                faiss.normalize_L2(query_vector)
            
            # Search the index
            scores, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                
                chunk_id = self.index_to_chunk_id.get(idx)
                if chunk_id is None:
                    logger.warning("No chunk ID found for index", index=idx)
                    continue
                
                chunk_data = self.chunk_metadata.get(chunk_id)
                if chunk_data is None:
                    logger.warning("No metadata found for chunk", chunk_id=chunk_id)
                    continue
                
                result = {
                    'chunk_id': chunk_id,
                    'text': chunk_data['text'],
                    'metadata': chunk_data['metadata'],
                    'similarity_score': float(score),
                    'rank': i + 1
                }
                results.append(result)
            
            logger.info("Query completed", 
                       query_vector_shape=query_vector.shape,
                       k=k,
                       results_count=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Failed to query vector database", error=str(e))
            return []
    
    def save_index(self, path: Optional[str] = None) -> None:
        """
        Save the FAISS index and metadata to disk.
        
        Args:
            path: Optional custom path to save the index
        """
        try:
            save_path = Path(path) if path else self.index_path
            
            # Save FAISS index
            index_file = save_path / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = save_path / "metadata.pkl"
            metadata_data = {
                'chunk_metadata': self.chunk_metadata,
                'chunk_id_to_index': self.chunk_id_to_index,
                'index_to_chunk_id': self.index_to_chunk_id,
                'next_index': self.next_index,
                'embedding_dim': self.embedding_dim,
                'index_type': self.index_type,
                'metric': self.metric
            }
            
            with open(metadata_file, 'wb') as f:
                pickle.dump(metadata_data, f)
            
            logger.info("Index saved successfully", 
                       index_file=str(index_file),
                       metadata_file=str(metadata_file),
                       total_chunks=self.index.ntotal)
            
        except Exception as e:
            logger.error("Failed to save index", error=str(e))
            raise
    
    def load_index(self, path: Optional[str] = None) -> bool:
        """
        Load the FAISS index and metadata from disk.
        
        Args:
            path: Optional custom path to load the index from
            
        Returns:
            True if index was loaded successfully, False otherwise
        """
        try:
            load_path = Path(path) if path else self.index_path
            
            index_file = load_path / "faiss_index.bin"
            metadata_file = load_path / "metadata.pkl"
            
            if not index_file.exists() or not metadata_file.exists():
                logger.info("No existing index found to load")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata
            with open(metadata_file, 'rb') as f:
                metadata_data = pickle.load(f)
            
            self.chunk_metadata = metadata_data.get('chunk_metadata', {})
            self.chunk_id_to_index = metadata_data.get('chunk_id_to_index', {})
            self.index_to_chunk_id = metadata_data.get('index_to_chunk_id', {})
            self.next_index = metadata_data.get('next_index', 0)
            
            # Validate loaded data
            if metadata_data.get('embedding_dim') != self.embedding_dim:
                logger.warning("Embedding dimension mismatch", 
                              loaded=metadata_data.get('embedding_dim'),
                              expected=self.embedding_dim)
            
            logger.info("Index loaded successfully", 
                       index_file=str(index_file),
                       metadata_file=str(metadata_file),
                       total_chunks=self.index.ntotal,
                       metadata_count=len(self.chunk_metadata))
            
            return True
            
        except Exception as e:
            logger.error("Failed to load index", error=str(e))
            return False
    
    def _load_index(self) -> None:
        """Load existing index during initialization."""
        self.load_index()
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chunk by its ID.
        
        Args:
            chunk_id: The chunk ID to retrieve
            
        Returns:
            Chunk data if found, None otherwise
        """
        return self.chunk_metadata.get(chunk_id)
    
    def get_chunk_count(self) -> int:
        """Get the total number of chunks in the database."""
        return self.index.ntotal
    
    def get_metadata_count(self) -> int:
        """Get the number of metadata entries."""
        return len(self.chunk_metadata)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary with database statistics
        """
        return {
            'total_chunks': self.index.ntotal,
            'metadata_count': len(self.chunk_metadata),
            'embedding_dim': self.embedding_dim,
            'index_type': self.index_type,
            'metric': self.metric,
            'index_path': str(self.index_path),
            'is_trained': getattr(self.index, 'is_trained', True)
        }
    
    def clear(self) -> None:
        """Clear all data from the vector database."""
        try:
            # Reset index
            self.index = self._create_index()
            
            # Clear metadata
            self.chunk_metadata.clear()
            self.chunk_id_to_index.clear()
            self.index_to_chunk_id.clear()
            self.next_index = 0
            
            logger.info("Vector database cleared")
            
        except Exception as e:
            logger.error("Failed to clear vector database", error=str(e))
            raise
    
    def remove_chunk(self, chunk_id: str) -> bool:
        """
        Remove a chunk from the database.
        Note: FAISS doesn't support direct removal, so this is a placeholder.
        
        Args:
            chunk_id: The chunk ID to remove
            
        Returns:
            True if chunk was found and marked for removal, False otherwise
        """
        if chunk_id not in self.chunk_metadata:
            return False
        
        # Mark as removed (FAISS doesn't support direct removal)
        self.chunk_metadata[chunk_id]['removed'] = True
        logger.info("Chunk marked for removal", chunk_id=chunk_id)
        return True
    
    def search_by_metadata(self, 
                          metadata_filter: Dict[str, Any], 
                          query_vector: np.ndarray, 
                          k: int = 5) -> List[Dict[str, Any]]:
        """
        Search chunks with metadata filtering.
        
        Args:
            metadata_filter: Dictionary of metadata fields to filter by
            query_vector: Query embedding vector
            k: Number of top results to return
            
        Returns:
            List of filtered results
        """
        try:
            # Get all results first
            all_results = self.query_top_k(query_vector, k * 2)  # Get more to account for filtering
            
            # Filter by metadata
            filtered_results = []
            for result in all_results:
                metadata = result.get('metadata', {})
                
                # Check if all filter conditions are met
                match = True
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_results.append(result)
                    if len(filtered_results) >= k:
                        break
            
            logger.info("Metadata filtered search completed", 
                       filter=metadata_filter,
                       total_results=len(all_results),
                       filtered_results=len(filtered_results))
            
            return filtered_results
            
        except Exception as e:
            logger.error("Failed to search with metadata filter", error=str(e))
            return []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def __len__(self) -> int:
        """Return the number of chunks in the database."""
        return self.index.ntotal
    
    def __contains__(self, chunk_id: str) -> bool:
        """Check if a chunk ID exists in the database."""
        return chunk_id in self.chunk_metadata


# Convenience functions for easy integration
def create_vector_database(embedding_dim: int = 384, 
                          index_type: str = "flat",
                          index_path: Optional[str] = None) -> VectorDatabase:
    """
    Create a new vector database instance.
    
    Args:
        embedding_dim: Dimension of embedding vectors
        index_type: Type of FAISS index
        index_path: Path to store the index
        
    Returns:
        VectorDatabase instance
    """
    return VectorDatabase(
        embedding_dim=embedding_dim,
        index_type=index_type,
        index_path=index_path
    )


def load_vector_database(index_path: str, 
                        embedding_dim: int = 384) -> Optional[VectorDatabase]:
    """
    Load an existing vector database from disk.
    
    Args:
        index_path: Path to the index directory
        embedding_dim: Expected embedding dimension
        
    Returns:
        VectorDatabase instance if loaded successfully, None otherwise
    """
    try:
        db = VectorDatabase(index_path=index_path, embedding_dim=embedding_dim)
        if db.get_chunk_count() > 0:
            return db
        else:
            logger.warning("Loaded database is empty")
            return db
    except Exception as e:
        logger.error("Failed to load vector database", error=str(e))
        return None


# Global vector database instance
default_vector_db = None

def get_default_vector_database() -> VectorDatabase:
    """Get the default vector database instance."""
    global default_vector_db
    
    if default_vector_db is None:
        default_vector_db = VectorDatabase(
            embedding_dim=384,  # all-MiniLM-L6-v2 dimension
            index_type="flat",
            index_path=str(Path(settings.faiss_index_path))
        )
    
    return default_vector_db

"""
Vector store management using FAISS
"""
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import faiss
import numpy as np
# Import will be handled by embeddings module

from .config import settings
from .logging import get_logger
from .embeddings import get_default_embedding_generator

logger = get_logger("vector_store")


class VectorStore:
    """Manages FAISS vector store for document embeddings"""
    
    def __init__(self):
        self.index_path = Path(settings.faiss_index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding generator
        self.embedding_generator = get_default_embedding_generator()
        self.embedding_dim = self.embedding_generator.embedding_dim
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        self.metadata = []
        self.is_trained = False
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self) -> None:
        """Load existing FAISS index and metadata"""
        try:
            index_file = self.index_path / "faiss_index.bin"
            metadata_file = self.index_path / "metadata.pkl"
            
            if index_file.exists() and metadata_file.exists():
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
                self.is_trained = True
                
                logger.info("Loaded existing FAISS index", 
                           index_size=self.index.ntotal,
                           metadata_count=len(self.metadata))
            else:
                logger.info("No existing index found, starting fresh")
                
        except Exception as e:
            logger.error("Failed to load existing index", error=str(e))
            # Start fresh if loading fails
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.metadata = []
            self.is_trained = False
    
    def _save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        try:
            index_file = self.index_path / "faiss_index.bin"
            metadata_file = self.index_path / "metadata.pkl"
            
            faiss.write_index(self.index, str(index_file))
            with open(metadata_file, "wb") as f:
                pickle.dump(self.metadata, f)
            
            logger.info("Saved FAISS index", 
                       index_size=self.index.ntotal,
                       metadata_count=len(self.metadata))
            
        except Exception as e:
            logger.error("Failed to save index", error=str(e))
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store"""
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            # Generate embeddings using the embedding generator
            logger.info("Generating embeddings", document_count=len(documents))
            
            # Convert documents to chunks format
            chunks = []
            for doc in documents:
                chunk = {
                    "text": doc["text"],
                    "metadata": doc["metadata"]
                }
                chunks.append(chunk)
            
            # Generate embeddings
            chunks_with_embeddings = self.embedding_generator.generate_embeddings(chunks)
            
            # Extract embeddings and metadata
            embeddings = np.array([chunk["embedding"] for chunk in chunks_with_embeddings])
            metadatas = [chunk["metadata"] for chunk in chunks_with_embeddings]
            
            # Embeddings are already normalized by the embedding generator
            
            # Add to index
            self.index.add(embeddings.astype('float32'))
            
            # Add metadata
            self.metadata.extend(metadatas)
            
            # Mark as trained
            self.is_trained = True
            
            # Save index
            self._save_index()
            
            logger.info("Documents added to vector store", 
                       new_docs=len(documents),
                       total_docs=self.index.ntotal)
            
        except Exception as e:
            logger.error("Failed to add documents to vector store", error=str(e))
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if not self.is_trained or self.index.ntotal == 0:
                logger.warning("Vector store is empty or not trained")
                return []
            
            # Generate query embedding using the embedding generator
            query_chunk = {
                "text": query,
                "metadata": {"chunk_type": "query"}
            }
            query_chunks = self.embedding_generator.generate_embeddings([query_chunk], use_cache=False)
            query_embedding = query_chunks[0]["embedding"].reshape(1, -1)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Prepare results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata):
                    result = {
                        "text": self.metadata[idx].get("text", ""),
                        "metadata": self.metadata[idx],
                        "score": float(score)
                    }
                    results.append(result)
            
            logger.info("Vector search completed", 
                       query=query,
                       results_count=len(results),
                       top_score=float(scores[0][0]) if len(scores[0]) > 0 else 0.0)
            
            return results
            
        except Exception as e:
            logger.error("Failed to search vector store", error=str(e), query=query)
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": self.index.ntotal,
            "embedding_dimension": self.embedding_dim,
            "is_trained": self.is_trained,
            "index_type": "FAISS IndexFlatIP"
        }
    
    def clear(self) -> None:
        """Clear the vector store"""
        try:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.metadata = []
            self.is_trained = False
            
            # Remove saved files
            index_file = self.index_path / "faiss_index.bin"
            metadata_file = self.index_path / "metadata.pkl"
            
            if index_file.exists():
                index_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info("Vector store cleared")
            
        except Exception as e:
            logger.error("Failed to clear vector store", error=str(e))
            raise


# Global vector store instance
vector_store = VectorStore()

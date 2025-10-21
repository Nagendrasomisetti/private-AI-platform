"""
Embedding Generation Module for PrivAI
Handles vector generation using sentence-transformers for text chunks
"""
import os
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

# Optional imports for embedding generation
try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .config import settings
from .logging import get_logger

logger = get_logger("embeddings")


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks using sentence-transformers.
    Supports CPU execution, quantization, and caching for optimal performance.
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 device: str = "cpu",
                 use_quantization: bool = False,
                 cache_dir: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
            device: Device to run on ('cpu' or 'cuda')
            use_quantization: Whether to use quantized embeddings for efficiency
            cache_dir: Directory to cache embeddings (optional)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for embedding generation. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.device = device
        self.use_quantization = use_quantization
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/embeddings_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model
        self.model = None
        self.embedding_dim = None
        self._load_model()
        
        logger.info("EmbeddingGenerator initialized", 
                   model_name=model_name,
                   device=device,
                   use_quantization=use_quantization,
                   cache_dir=str(self.cache_dir))
    
    def _load_model(self) -> None:
        """Load the sentence-transformer model."""
        try:
            logger.info("Loading sentence-transformer model", model=self.model_name)
            
            # Load model with device specification
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            # Get embedding dimension
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            # Apply quantization if requested
            if self.use_quantization and TORCH_AVAILABLE:
                self._apply_quantization()
            
            logger.info("Model loaded successfully", 
                       model=self.model_name,
                       embedding_dim=self.embedding_dim,
                       device=self.device)
            
        except Exception as e:
            logger.error("Failed to load sentence-transformer model", 
                        model=self.model_name, 
                        error=str(e))
            raise
    
    def _apply_quantization(self) -> None:
        """Apply quantization to the model for efficiency."""
        try:
            if TORCH_AVAILABLE and hasattr(self.model, 'encode'):
                logger.info("Applying quantization to model")
                # Note: Actual quantization would require more complex implementation
                # This is a placeholder for future quantization features
                logger.info("Quantization applied (placeholder)")
        except Exception as e:
            logger.warning("Failed to apply quantization", error=str(e))
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]], 
                           batch_size: int = 32,
                           use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of text chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
            batch_size: Batch size for processing (default: 32)
            use_cache: Whether to use cached embeddings if available
            
        Returns:
            List of chunk dictionaries with added 'embedding' field
        """
        try:
            if not chunks:
                logger.warning("No chunks provided for embedding generation")
                return []
            
            logger.info("Generating embeddings", 
                       chunk_count=len(chunks),
                       batch_size=batch_size,
                       use_cache=use_cache)
            
            # Extract texts and check cache
            texts = []
            cached_embeddings = {}
            uncached_indices = []
            
            if use_cache:
                for i, chunk in enumerate(chunks):
                    cache_key = self._get_cache_key(chunk)
                    cached_embedding = self._load_cached_embedding(cache_key)
                    
                    if cached_embedding is not None:
                        cached_embeddings[i] = cached_embedding
                        logger.debug("Using cached embedding", chunk_index=i)
                    else:
                        texts.append(chunk['text'])
                        uncached_indices.append(i)
            else:
                texts = [chunk['text'] for chunk in chunks]
                uncached_indices = list(range(len(chunks)))
            
            # Generate embeddings for uncached chunks
            new_embeddings = {}
            if texts:
                logger.info("Generating new embeddings", count=len(texts))
                embeddings = self._generate_batch_embeddings(texts, batch_size)
                
                for i, embedding in enumerate(embeddings):
                    chunk_index = uncached_indices[i]
                    new_embeddings[chunk_index] = embedding
                    
                    # Cache the embedding
                    if use_cache:
                        cache_key = self._get_cache_key(chunks[chunk_index])
                        self._save_cached_embedding(cache_key, embedding)
            
            # Combine cached and new embeddings
            result_chunks = []
            for i, chunk in enumerate(chunks):
                result_chunk = chunk.copy()
                
                if i in cached_embeddings:
                    result_chunk['embedding'] = cached_embeddings[i]
                elif i in new_embeddings:
                    result_chunk['embedding'] = new_embeddings[i]
                else:
                    logger.error("No embedding found for chunk", chunk_index=i)
                    continue
                
                result_chunks.append(result_chunk)
            
            logger.info("Embedding generation completed", 
                       total_chunks=len(chunks),
                       cached_embeddings=len(cached_embeddings),
                       new_embeddings=len(new_embeddings))
            
            return result_chunks
            
        except Exception as e:
            logger.error("Failed to generate embeddings", error=str(e))
            raise
    
    def _generate_batch_embeddings(self, texts: List[str], batch_size: int) -> List[np.ndarray]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of normalized embedding vectors
        """
        try:
            logger.info("Generating batch embeddings", 
                       text_count=len(texts),
                       batch_size=batch_size)
            
            # Generate embeddings in batches
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                logger.debug("Processing batch", 
                           batch_start=i,
                           batch_size=len(batch_texts))
                
                # Generate embeddings for this batch
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_tensor=False,
                    show_progress_bar=False,
                    normalize_embeddings=True  # Normalize for cosine similarity
                )
                
                all_embeddings.extend(batch_embeddings)
            
            logger.info("Batch embedding generation completed", 
                       total_embeddings=len(all_embeddings))
            
            return all_embeddings
            
        except Exception as e:
            logger.error("Failed to generate batch embeddings", error=str(e))
            raise
    
    def _get_cache_key(self, chunk: Dict[str, Any]) -> str:
        """
        Generate a cache key for a chunk.
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            Cache key string
        """
        # Create a unique key based on text content and metadata
        text = chunk['text']
        metadata = chunk.get('metadata', {})
        
        # Include relevant metadata in the key
        key_data = {
            'text': text,
            'model_name': self.model_name,
            'chunk_size': metadata.get('chunk_size', 500),
            'chunk_overlap': metadata.get('chunk_overlap', 50)
        }
        
        # Generate hash
        key_string = str(sorted(key_data.items()))
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _load_cached_embedding(self, cache_key: str) -> Optional[np.ndarray]:
        """
        Load a cached embedding.
        
        Args:
            cache_key: Cache key for the embedding
            
        Returns:
            Cached embedding array or None if not found
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    embedding = pickle.load(f)
                
                logger.debug("Loaded cached embedding", cache_key=cache_key)
                return embedding
            
            return None
            
        except Exception as e:
            logger.warning("Failed to load cached embedding", 
                          cache_key=cache_key, 
                          error=str(e))
            return None
    
    def _save_cached_embedding(self, cache_key: str, embedding: np.ndarray) -> None:
        """
        Save an embedding to cache.
        
        Args:
            cache_key: Cache key for the embedding
            embedding: Embedding array to cache
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
            
            logger.debug("Saved embedding to cache", cache_key=cache_key)
            
        except Exception as e:
            logger.warning("Failed to save embedding to cache", 
                          cache_key=cache_key, 
                          error=str(e))
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # Use sentence-transformers utility
                similarity = cos_sim(embedding1, embedding2).item()
            else:
                # Manual cosine similarity calculation
                dot_product = np.dot(embedding1, embedding2)
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                similarity = dot_product / (norm1 * norm2)
            
            return float(similarity)
            
        except Exception as e:
            logger.error("Failed to compute similarity", error=str(e))
            return 0.0
    
    def find_similar_chunks(self, query_embedding: np.ndarray, 
                           chunk_embeddings: List[Dict[str, Any]], 
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find the most similar chunks to a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            chunk_embeddings: List of chunks with embeddings
            top_k: Number of top similar chunks to return
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            similarities = []
            
            for chunk in chunk_embeddings:
                if 'embedding' not in chunk:
                    logger.warning("Chunk missing embedding", chunk_id=chunk.get('metadata', {}).get('chunk_index'))
                    continue
                
                similarity = self.compute_similarity(query_embedding, chunk['embedding'])
                similarities.append((chunk, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k results
            results = []
            for chunk, similarity in similarities[:top_k]:
                result_chunk = chunk.copy()
                result_chunk['similarity_score'] = similarity
                results.append(result_chunk)
            
            logger.info("Found similar chunks", 
                       query_embedding_shape=query_embedding.shape,
                       total_chunks=len(chunk_embeddings),
                       top_k=top_k,
                       results_count=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Failed to find similar chunks", error=str(e))
            return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embedding generator.
        
        Returns:
            Dictionary with embedding statistics
        """
        try:
            stats = {
                "model_name": self.model_name,
                "device": self.device,
                "embedding_dimension": self.embedding_dim,
                "use_quantization": self.use_quantization,
                "cache_directory": str(self.cache_dir),
                "cache_enabled": True
            }
            
            # Count cached embeddings
            if self.cache_dir.exists():
                cache_files = list(self.cache_dir.glob("*.pkl"))
                stats["cached_embeddings"] = len(cache_files)
            else:
                stats["cached_embeddings"] = 0
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get embedding stats", error=str(e))
            return {}
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        try:
            if self.cache_dir.exists():
                cache_files = list(self.cache_dir.glob("*.pkl"))
                for cache_file in cache_files:
                    cache_file.unlink()
                
                logger.info("Embedding cache cleared", files_removed=len(cache_files))
            else:
                logger.info("No cache to clear")
                
        except Exception as e:
            logger.error("Failed to clear embedding cache", error=str(e))


# Convenience functions for easy integration
def generate_embeddings_for_chunks(chunks: List[Dict[str, Any]], 
                                  model_name: str = "all-MiniLM-L6-v2",
                                  device: str = "cpu",
                                  batch_size: int = 32) -> List[Dict[str, Any]]:
    """
    Convenience function to generate embeddings for chunks.
    
    Args:
        chunks: List of chunk dictionaries
        model_name: Sentence-transformer model name
        device: Device to run on
        batch_size: Batch size for processing
        
    Returns:
        List of chunks with embeddings
    """
    generator = EmbeddingGenerator(model_name=model_name, device=device)
    return generator.generate_embeddings(chunks, batch_size=batch_size)


def generate_query_embedding(query: str, 
                           model_name: str = "all-MiniLM-L6-v2",
                           device: str = "cpu") -> np.ndarray:
    """
    Generate embedding for a single query string.
    
    Args:
        query: Query text
        model_name: Sentence-transformer model name
        device: Device to run on
        
    Returns:
        Query embedding vector
    """
    generator = EmbeddingGenerator(model_name=model_name, device=device)
    
    # Create a temporary chunk for the query
    query_chunk = {
        'text': query,
        'metadata': {
            'chunk_type': 'query',
            'chunk_index': 0
        }
    }
    
    # Generate embedding
    result = generator.generate_embeddings([query_chunk], use_cache=False)
    
    if result and 'embedding' in result[0]:
        return result[0]['embedding']
    else:
        raise ValueError("Failed to generate query embedding")


# Global embedding generator instance
default_embedding_generator = None

def get_default_embedding_generator() -> EmbeddingGenerator:
    """Get the default embedding generator instance."""
    global default_embedding_generator
    
    if default_embedding_generator is None:
        default_embedding_generator = EmbeddingGenerator(
            model_name=settings.embedding_model,
            device="cpu",
            use_quantization=False,
            cache_dir=str(Path(settings.faiss_index_path) / "embeddings_cache")
        )
    
    return default_embedding_generator

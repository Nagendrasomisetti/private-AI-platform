"""
RAG (Retrieval-Augmented Generation) Module for PrivAI
Handles query embedding, FAISS retrieval, and LLM prompting with local and API fallback
"""
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

# Optional imports for LLM integration
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TORCH_AVAILABLE = True
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import settings
from .logging import get_logger
from .embeddings import get_default_embedding_generator
from .vector_db import get_default_vector_database

logger = get_logger("rag")


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for PrivAI.
    Handles query processing, document retrieval, and LLM response generation.
    """
    
    def __init__(self, 
                 embedding_generator=None,
                 vector_database=None,
                 local_model_name: str = "microsoft/DialoGPT-medium",
                 openai_api_key: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the RAG pipeline.
        
        Args:
            embedding_generator: Embedding generator instance
            vector_database: Vector database instance
            local_model_name: Name of local LLM model
            openai_api_key: OpenAI API key for fallback
            cache_dir: Directory for caching responses
        """
        self.embedding_generator = embedding_generator or get_default_embedding_generator()
        self.vector_database = vector_database or get_default_vector_database()
        self.local_model_name = local_model_name
        self.openai_api_key = openai_api_key or settings.openai_api_key
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/rag_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM components
        self.local_llm = None
        self.openai_client = None
        self._initialize_llm()
        
        # Prompt template
        self.prompt_template = self._create_prompt_template()
        
        logger.info("RAGPipeline initialized", 
                   local_model=local_model_name,
                   openai_available=OPENAI_AVAILABLE,
                   cache_dir=str(self.cache_dir))
    
    def _initialize_llm(self) -> None:
        """Initialize local LLM and OpenAI client."""
        try:
            # Initialize local LLM
            if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
                logger.info("Loading local LLM", model=self.local_model_name)
                self.local_llm = pipeline(
                    "text-generation",
                    model=self.local_model_name,
                    tokenizer=self.local_model_name,
                    device=0 if torch.cuda.is_available() else -1,
                    max_length=512,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=50256  # GPT-2 pad token
                )
                logger.info("Local LLM loaded successfully")
            else:
                logger.warning("Local LLM not available - install transformers and torch")
            
            # Initialize OpenAI client
            if OPENAI_AVAILABLE and self.openai_api_key:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OpenAI client not available - no API key provided")
                
        except Exception as e:
            logger.error("Failed to initialize LLM components", error=str(e))
    
    def _create_prompt_template(self) -> str:
        """Create the prompt template for LLM."""
        return """You are a helpful assistant with access to the following college documents:

{retrieved_chunks}

Question: {user_query}

Instructions:
- Answer the question concisely and accurately based on the provided documents
- Use specific information from the documents when possible
- If the answer is not in the documents, say so clearly
- Include relevant references to document sources
- Keep your response focused and helpful

Answer:"""
    
    def query(self, 
              user_query: str, 
              top_k: int = 5,
              use_local_llm: bool = True,
              use_cache: bool = True) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            user_query: The user's question
            top_k: Number of top chunks to retrieve
            use_local_llm: Whether to use local LLM or API fallback
            use_cache: Whether to use cached responses
            
        Returns:
            Dictionary containing answer, sources, and metadata
        """
        try:
            start_time = time.time()
            
            logger.info("Processing RAG query", 
                       query=user_query[:100] + "..." if len(user_query) > 100 else user_query,
                       top_k=top_k,
                       use_local_llm=use_local_llm)
            
            # Check cache first
            if use_cache:
                cached_response = self._get_cached_response(user_query, top_k)
                if cached_response:
                    logger.info("Using cached response")
                    return cached_response
            
            # Step 1: Generate query embedding
            query_embedding = self._generate_query_embedding(user_query)
            
            # Step 2: Retrieve relevant chunks
            retrieved_chunks = self._retrieve_chunks(query_embedding, top_k)
            
            if not retrieved_chunks:
                return {
                    "answer": "I don't have any relevant documents to answer your question. Please make sure you have uploaded and processed some documents first.",
                    "sources": [],
                    "metadata": {
                        "query": user_query,
                        "retrieved_chunks": 0,
                        "processing_time": time.time() - start_time,
                        "model_used": "none",
                        "cached": False
                    }
                }
            
            # Step 3: Construct prompt
            prompt = self._construct_prompt(user_query, retrieved_chunks)
            
            # Step 4: Generate response using LLM
            response = self._generate_response(prompt, use_local_llm)
            
            # Step 5: Process response and extract sources
            answer, sources = self._process_response(response, retrieved_chunks)
            
            # Step 6: Create final result
            result = {
                "answer": answer,
                "sources": sources,
                "metadata": {
                    "query": user_query,
                    "retrieved_chunks": len(retrieved_chunks),
                    "processing_time": time.time() - start_time,
                    "model_used": "local" if use_local_llm else "openai",
                    "cached": False
                }
            }
            
            # Cache the response
            if use_cache:
                self._cache_response(user_query, top_k, result)
            
            logger.info("RAG query completed", 
                       processing_time=result["metadata"]["processing_time"],
                       retrieved_chunks=len(retrieved_chunks),
                       sources=len(sources))
            
            return result
            
        except Exception as e:
            logger.error("RAG query failed", error=str(e), query=user_query)
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "metadata": {
                    "query": user_query,
                    "retrieved_chunks": 0,
                    "processing_time": time.time() - start_time,
                    "model_used": "error",
                    "cached": False,
                    "error": str(e)
                }
            }
    
    def _generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for the user query."""
        try:
            # Create query chunk
            query_chunk = {
                "text": query,
                "metadata": {"chunk_type": "query"}
            }
            
            # Generate embedding
            query_chunks = self.embedding_generator.generate_embeddings([query_chunk], use_cache=False)
            
            if not query_chunks or 'embedding' not in query_chunks[0]:
                raise ValueError("Failed to generate query embedding")
            
            return query_chunks[0]['embedding']
            
        except Exception as e:
            logger.error("Failed to generate query embedding", error=str(e))
            raise
    
    def _retrieve_chunks(self, query_embedding: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks from vector database."""
        try:
            results = self.vector_database.query_top_k(query_embedding, top_k)
            
            # Convert results to chunk format
            chunks = []
            for result in results:
                chunk = {
                    "text": result["text"],
                    "metadata": result["metadata"],
                    "similarity_score": result["similarity_score"],
                    "rank": result["rank"]
                }
                chunks.append(chunk)
            
            logger.info("Retrieved chunks", count=len(chunks))
            return chunks
            
        except Exception as e:
            logger.error("Failed to retrieve chunks", error=str(e))
            return []
    
    def _construct_prompt(self, user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Construct the prompt for the LLM."""
        try:
            # Format retrieved chunks
            chunks_text = ""
            for i, chunk in enumerate(retrieved_chunks, 1):
                source = chunk["metadata"].get("source_file", "Unknown")
                page = chunk["metadata"].get("page_number", "N/A")
                similarity = chunk["similarity_score"]
                
                chunks_text += f"\n--- Document {i} (Source: {source}, Page: {page}, Relevance: {similarity:.3f}) ---\n"
                chunks_text += f"{chunk['text']}\n"
            
            # Format the prompt
            prompt = self.prompt_template.format(
                retrieved_chunks=chunks_text,
                user_query=user_query
            )
            
            return prompt
            
        except Exception as e:
            logger.error("Failed to construct prompt", error=str(e))
            return f"Question: {user_query}\n\nAnswer:"
    
    def _generate_response(self, prompt: str, use_local_llm: bool) -> str:
        """Generate response using local LLM or API fallback."""
        try:
            if use_local_llm and self.local_llm:
                return self._generate_local_response(prompt)
            elif self.openai_client:
                return self._generate_openai_response(prompt)
            else:
                return self._generate_fallback_response(prompt)
                
        except Exception as e:
            logger.error("Failed to generate response", error=str(e))
            return "I apologize, but I'm unable to generate a response at this time."
    
    def _generate_local_response(self, prompt: str) -> str:
        """Generate response using local LLM."""
        try:
            logger.info("Generating response with local LLM")
            
            # Generate response
            response = self.local_llm(
                prompt,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.local_llm.tokenizer.eos_token_id
            )
            
            # Extract the generated text
            generated_text = response[0]['generated_text']
            
            # Remove the prompt from the response
            if generated_text.startswith(prompt):
                answer = generated_text[len(prompt):].strip()
            else:
                answer = generated_text.strip()
            
            logger.info("Local LLM response generated", length=len(answer))
            return answer
            
        except Exception as e:
            logger.error("Failed to generate local response", error=str(e))
            raise
    
    def _generate_openai_response(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            logger.info("Generating response with OpenAI")
            
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for college students. Answer questions based on the provided documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            logger.info("OpenAI response generated", length=len(answer))
            return answer
            
        except Exception as e:
            logger.error("Failed to generate OpenAI response", error=str(e))
            raise
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when no LLM is available."""
        logger.warning("No LLM available, using fallback response")
        
        # Extract the question from the prompt
        if "Question:" in prompt:
            question = prompt.split("Question:")[1].split("\n")[0].strip()
        else:
            question = "your question"
        
        return f"I understand you're asking about: {question}. However, I don't have access to an AI model to provide a detailed answer. Please check your configuration and ensure either a local model or API key is available."
    
    def _process_response(self, response: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Process the LLM response and extract source references."""
        try:
            # Clean up the response
            answer = response.strip()
            
            # Create source references
            sources = []
            for chunk in retrieved_chunks:
                source = {
                    "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                    "metadata": chunk["metadata"],
                    "similarity_score": chunk["similarity_score"],
                    "rank": chunk["rank"]
                }
                sources.append(source)
            
            return answer, sources
            
        except Exception as e:
            logger.error("Failed to process response", error=str(e))
            return response, []
    
    def _get_cache_key(self, query: str, top_k: int) -> str:
        """Generate cache key for query."""
        cache_data = f"{query}_{top_k}_{self.local_model_name}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cached_response(self, query: str, top_k: int) -> Optional[Dict[str, Any]]:
        """Get cached response if available."""
        try:
            cache_key = self._get_cache_key(query, top_k)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Mark as cached
                cached_data["metadata"]["cached"] = True
                
                logger.debug("Retrieved cached response", cache_key=cache_key)
                return cached_data
            
            return None
            
        except Exception as e:
            logger.warning("Failed to retrieve cached response", error=str(e))
            return None
    
    def _cache_response(self, query: str, top_k: int, response: Dict[str, Any]) -> None:
        """Cache the response for future use."""
        try:
            cache_key = self._get_cache_key(query, top_k)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Add cache metadata
            response["metadata"]["cached_at"] = datetime.now().isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            
            logger.debug("Cached response", cache_key=cache_key)
            
        except Exception as e:
            logger.warning("Failed to cache response", error=str(e))
    
    def clear_cache(self) -> None:
        """Clear all cached responses."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            for cache_file in cache_files:
                cache_file.unlink()
            
            logger.info("RAG cache cleared", files_removed=len(cache_files))
            
        except Exception as e:
            logger.error("Failed to clear cache", error=str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics."""
        try:
            stats = {
                "local_llm_available": self.local_llm is not None,
                "openai_available": self.openai_client is not None,
                "local_model_name": self.local_model_name,
                "cache_directory": str(self.cache_dir),
                "embedding_generator": self.embedding_generator.get_embedding_stats(),
                "vector_database": self.vector_database.get_stats()
            }
            
            # Count cached responses
            cache_files = list(self.cache_dir.glob("*.json"))
            stats["cached_responses"] = len(cache_files)
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get RAG stats", error=str(e))
            return {}


# Convenience functions for easy integration
def create_rag_pipeline(local_model_name: str = "microsoft/DialoGPT-medium",
                       openai_api_key: Optional[str] = None,
                       cache_dir: Optional[str] = None) -> RAGPipeline:
    """
    Create a new RAG pipeline instance.
    
    Args:
        local_model_name: Name of local LLM model
        openai_api_key: OpenAI API key for fallback
        cache_dir: Directory for caching responses
        
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(
        local_model_name=local_model_name,
        openai_api_key=openai_api_key,
        cache_dir=cache_dir
    )


def query_rag(user_query: str, 
              top_k: int = 5,
              use_local_llm: bool = True,
              rag_pipeline: Optional[RAGPipeline] = None) -> Dict[str, Any]:
    """
    Convenience function to query the RAG pipeline.
    
    Args:
        user_query: The user's question
        top_k: Number of top chunks to retrieve
        use_local_llm: Whether to use local LLM or API fallback
        rag_pipeline: RAG pipeline instance (creates default if None)
        
    Returns:
        Dictionary containing answer, sources, and metadata
    """
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline()
    
    return rag_pipeline.query(user_query, top_k, use_local_llm)


# Global RAG pipeline instance
default_rag_pipeline = None

def get_default_rag_pipeline() -> RAGPipeline:
    """Get the default RAG pipeline instance."""
    global default_rag_pipeline
    
    if default_rag_pipeline is None:
        default_rag_pipeline = RAGPipeline()
    
    return default_rag_pipeline

"""
LLM service for generating responses
"""
import time
from typing import List, Dict, Any, Optional

import openai
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from .config import settings
from .logging import get_logger

logger = get_logger("llm_service")


class LLMService:
    """Handles LLM interactions for generating responses"""
    
    def __init__(self):
        self.local_model = None
        self.local_tokenizer = None
        self.openai_client = None
        
        # Initialize OpenAI client if API key is provided
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("No OpenAI API key provided, using local model only")
    
    def _load_local_model(self) -> None:
        """Load local LLM model"""
        try:
            if self.local_model is None:
                logger.info("Loading local LLM model", model=settings.local_llm_model)
                self.local_tokenizer = AutoTokenizer.from_pretrained(settings.local_llm_model)
                self.local_model = AutoModelForCausalLM.from_pretrained(settings.local_llm_model)
                
                # Add padding token if not present
                if self.local_tokenizer.pad_token is None:
                    self.local_tokenizer.pad_token = self.local_tokenizer.eos_token
                
                logger.info("Local LLM model loaded successfully")
        except Exception as e:
            logger.error("Failed to load local LLM model", error=str(e))
            raise
    
    def _generate_with_local_model(self, prompt: str, max_length: int = 512) -> str:
        """Generate response using local model"""
        try:
            if self.local_model is None:
                self._load_local_model()
            
            # Tokenize input
            inputs = self.local_tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            # Generate response
            with torch.no_grad():
                outputs = self.local_model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.local_tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            logger.info("Generated response with local model", 
                       prompt_length=len(prompt),
                       response_length=len(response))
            
            return response
            
        except Exception as e:
            logger.error("Failed to generate response with local model", error=str(e))
            raise
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI API"""
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not initialized")
            
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for college students. Answer questions based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            logger.info("Generated response with OpenAI", 
                       prompt_length=len(prompt),
                       response_length=len(answer))
            
            return answer
            
        except Exception as e:
            logger.error("Failed to generate response with OpenAI", error=str(e))
            raise
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]], 
                         use_local: bool = True) -> Dict[str, Any]:
        """Generate response to user query"""
        start_time = time.time()
        
        try:
            # Prepare context from chunks
            context = "\n\n".join([chunk["text"] for chunk in context_chunks])
            
            # Create prompt
            prompt = f"""Context:
{context}

Question: {query}

Answer:"""
            
            # Generate response
            if use_local and self.local_model is not None:
                answer = self._generate_with_local_model(prompt)
                model_used = "local"
            elif self.openai_client:
                answer = self._generate_with_openai(prompt)
                model_used = "openai"
            else:
                # Fallback to simple response
                answer = "I apologize, but I don't have access to an AI model to answer your question. Please check your configuration."
                model_used = "none"
            
            processing_time = time.time() - start_time
            
            # Prepare sources
            sources = []
            for chunk in context_chunks:
                source = {
                    "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                    "score": chunk.get("score", 0.0),
                    "metadata": chunk.get("metadata", {})
                }
                sources.append(source)
            
            result = {
                "answer": answer,
                "sources": sources,
                "processing_time": processing_time,
                "model_used": model_used
            }
            
            logger.info("Response generated successfully", 
                       query=query,
                       context_chunks=len(context_chunks),
                       processing_time=processing_time,
                       model_used=model_used)
            
            return result
            
        except Exception as e:
            logger.error("Failed to generate response", error=str(e), query=query)
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "processing_time": time.time() - start_time,
                "model_used": "error"
            }


# Global LLM service instance
llm_service = LLMService()

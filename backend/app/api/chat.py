"""
Chat API endpoints for AI interactions
"""
from fastapi import APIRouter, HTTPException

from ..models.schemas import ChatRequest, ChatResponse, ErrorResponse
from ..core.vector_store import vector_store
from ..core.llm_service import llm_service
from ..core.logging import get_logger

logger = get_logger("chat_api")
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat query and return AI response
    
    Args:
        request: Chat request with query and parameters
        
    Returns:
        ChatResponse: AI response with sources and metadata
    """
    try:
        logger.info("Chat request received", 
                   query=request.query[:100] + "..." if len(request.query) > 100 else request.query,
                   top_k=request.top_k,
                   use_local_llm=request.use_local_llm)
        
        # Validate query
        if not request.query or not request.query.strip():
            raise ValueError("Query cannot be empty")
        
        # Search for relevant documents
        context_chunks = vector_store.search(request.query, top_k=request.top_k)
        
        if not context_chunks:
            logger.warning("No relevant context found for query", query=request.query)
            return ChatResponse(
                answer="I don't have enough information to answer your question. Please make sure you have uploaded and ingested some documents first.",
                sources=[],
                processing_time=0.0,
                model_used="none"
            )
        
        # Generate response using LLM
        response_data = llm_service.generate_response(
            query=request.query,
            context_chunks=context_chunks,
            use_local=request.use_local_llm
        )
        
        response = ChatResponse(
            answer=response_data["answer"],
            sources=response_data["sources"],
            processing_time=response_data["processing_time"],
            model_used=response_data["model_used"]
        )
        
        logger.info("Chat response generated successfully",
                   query=request.query[:50],
                   answer_length=len(response.answer),
                   sources_count=len(response.sources),
                   processing_time=response.processing_time,
                   model_used=response.model_used)
        
        return response
        
    except ValueError as e:
        logger.error("Chat request validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error("Chat request failed", error=str(e), query=request.query)
        raise HTTPException(status_code=500, detail=f"Chat request failed: {str(e)}")


@router.get("/health")
async def chat_health():
    """
    Check the health of the chat service
    
    Returns:
        dict: Health status of chat components
    """
    try:
        logger.info("Chat health check requested")
        
        # Check vector store
        vector_stats = vector_store.get_stats()
        
        # Check LLM service
        llm_status = "available"
        try:
            # Try to generate a simple test response
            test_response = llm_service.generate_response(
                query="test",
                context_chunks=[{"text": "test context", "metadata": {}}],
                use_local=True
            )
            llm_status = "working"
        except Exception as e:
            llm_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "vector_store": {
                "status": "available",
                "total_documents": vector_stats["total_documents"],
                "is_trained": vector_stats["is_trained"]
            },
            "llm_service": {
                "status": llm_status
            },
            "message": "Chat service is operational"
        }
        
    except Exception as e:
        logger.error("Chat health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Chat service is not operational"
        }


@router.get("/stats")
async def get_chat_stats():
    """
    Get statistics about the chat system
    
    Returns:
        dict: Chat system statistics
    """
    try:
        logger.info("Chat stats requested")
        
        vector_stats = vector_store.get_stats()
        
        return {
            "vector_store": vector_stats,
            "supported_models": {
                "local": "microsoft/DialoGPT-medium",
                "openai": "gpt-3.5-turbo"
            },
            "max_context_chunks": 10,
            "default_top_k": 5
        }
        
    except Exception as e:
        logger.error("Failed to get chat stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get chat stats")

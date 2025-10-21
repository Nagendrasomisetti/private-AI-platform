# PrivAI RAG (Retrieval-Augmented Generation) Module

A comprehensive RAG pipeline for PrivAI that integrates query embedding, FAISS retrieval, and LLM prompting with local and API fallback options.

## Features

### 🔍 **Query Processing**
- **Query Embedding**: Convert user queries to vector embeddings
- **FAISS Retrieval**: Retrieve top-k most relevant chunks
- **Semantic Search**: Find relevant content by meaning, not just keywords
- **Configurable Top-K**: Adjustable number of retrieved chunks

### 🤖 **LLM Integration**
- **Local LLM Support**: Integration with LLaMA, Mistral, and other local models
- **API Fallback**: OpenAI API integration for cloud-based responses
- **Model Selection**: Choose between local and cloud-based models
- **Response Generation**: Context-aware answer generation

### 📝 **Prompt Engineering**
- **Template System**: Configurable prompt templates
- **Context Integration**: Seamless integration of retrieved chunks
- **Source References**: Automatic source citation and referencing
- **Instruction Following**: Clear instructions for LLM behavior

### 💾 **Caching System**
- **Query Caching**: Cache responses for repeated queries
- **Performance Optimization**: Significant speedup for cached queries
- **Cache Management**: Clear and manage cached responses
- **Persistent Storage**: Cache survives application restarts

### 🔗 **Source Tracking**
- **Source References**: Track and display document sources
- **Similarity Scores**: Show relevance scores for retrieved chunks
- **Metadata Preservation**: Maintain rich metadata for sources
- **Citation Formatting**: Proper citation formatting for sources

## Usage

### Basic Usage

```python
from app.core.rag import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(
    local_model_name="microsoft/DialoGPT-medium",
    openai_api_key="your-api-key"  # Optional
)

# Process a query
result = rag.query("How does PrivAI ensure privacy?", top_k=5)

print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

### Advanced Usage

```python
# Create RAG pipeline with custom settings
rag = RAGPipeline(
    local_model_name="microsoft/DialoGPT-medium",
    openai_api_key="your-openai-key",
    cache_dir="custom_cache"
)

# Process query with specific parameters
result = rag.query(
    user_query="What file types are supported?",
    top_k=3,
    use_local_llm=True,
    use_cache=True
)

# Access detailed results
answer = result['answer']
sources = result['sources']
metadata = result['metadata']

# Show sources
for source in sources:
    print(f"Source: {source['metadata']['source_file']}")
    print(f"Similarity: {source['similarity_score']:.3f}")
    print(f"Text: {source['text'][:100]}...")
```

### Convenience Functions

```python
from app.core.rag import query_rag, create_rag_pipeline

# Simple query function
result = query_rag("What is PrivAI?", top_k=3)

# Create custom pipeline
rag = create_rag_pipeline(
    local_model_name="gpt2",
    cache_dir="my_cache"
)
```

## API Reference

### RAGPipeline Class

#### `__init__(embedding_generator, vector_database, local_model_name, openai_api_key, cache_dir)`
Initialize the RAG pipeline.

**Parameters:**
- `embedding_generator`: Embedding generator instance
- `vector_database`: Vector database instance
- `local_model_name` (str): Name of local LLM model
- `openai_api_key` (str): OpenAI API key for fallback
- `cache_dir` (str): Directory for caching responses

#### `query(user_query, top_k, use_local_llm, use_cache) -> Dict[str, Any]`
Process a user query through the RAG pipeline.

**Parameters:**
- `user_query` (str): The user's question
- `top_k` (int): Number of top chunks to retrieve
- `use_local_llm` (bool): Whether to use local LLM or API fallback
- `use_cache` (bool): Whether to use cached responses

**Returns:**
- `Dict[str, Any]`: Dictionary containing answer, sources, and metadata

#### `clear_cache() -> None`
Clear all cached responses.

#### `get_stats() -> Dict[str, Any]`
Get RAG pipeline statistics.

### Convenience Functions

#### `create_rag_pipeline(local_model_name, openai_api_key, cache_dir)`
Create a new RAG pipeline instance.

#### `query_rag(user_query, top_k, use_local_llm, rag_pipeline)`
Convenience function to query the RAG pipeline.

#### `get_default_rag_pipeline()`
Get the default RAG pipeline instance.

## Prompt Template

The RAG pipeline uses a configurable prompt template:

```
You are a helpful assistant with access to the following college documents:

{retrieved_chunks}

Question: {user_query}

Instructions:
- Answer the question concisely and accurately based on the provided documents
- Use specific information from the documents when possible
- If the answer is not in the documents, say so clearly
- Include relevant references to document sources
- Keep your response focused and helpful

Answer:
```

## Model Support

### Local Models
- **DialoGPT**: `microsoft/DialoGPT-medium`
- **GPT-2**: `gpt2`, `gpt2-medium`, `gpt2-large`
- **DistilGPT-2**: `distilgpt2`
- **Custom Models**: Any Hugging Face model

### API Models
- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`
- **Custom APIs**: Extensible for other providers

## Caching System

### Cache Key Generation
Cache keys are generated using:
- User query text
- Top-k value
- Model name
- MD5 hash for uniqueness

### Cache Storage
- **Format**: JSON files
- **Location**: Configurable cache directory
- **Persistence**: Survives application restarts
- **Management**: Automatic cleanup and statistics

### Cache Benefits
- **Performance**: 10x+ speedup for repeated queries
- **Cost Savings**: Reduces API calls
- **Reliability**: Works offline for cached queries

## Source References

### Source Information
Each source includes:
- **Text**: Chunk text content
- **Metadata**: Document metadata
- **Similarity Score**: Relevance score (0-1)
- **Rank**: Position in results

### Source Format
```python
{
    "text": "Document content...",
    "metadata": {
        "source_file": "document.pdf",
        "page_number": 1,
        "chunk_type": "document"
    },
    "similarity_score": 0.85,
    "rank": 1
}
```

## Error Handling

The RAG pipeline includes comprehensive error handling:
- **Import Errors**: Graceful handling of missing dependencies
- **Model Errors**: Fallback to alternative models
- **Query Errors**: Robust query processing
- **Cache Errors**: Fallback when caching fails

## Performance

### Benchmarks
- **Query Processing**: ~2-5 seconds (local LLM)
- **Cache Hit**: ~0.1-0.5 seconds
- **API Fallback**: ~1-3 seconds
- **Memory Usage**: ~2-4GB (with local model)

### Optimization Tips
1. **Use Caching**: Enable caching for repeated queries
2. **Choose Top-K**: Balance relevance vs. processing time
3. **Model Selection**: Use appropriate model for your needs
4. **Batch Processing**: Process multiple queries together

## Integration

### FastAPI Integration
The RAG module integrates seamlessly with the PrivAI backend:

```python
from app.core.rag import get_default_rag_pipeline

# Use default RAG pipeline
rag = get_default_rag_pipeline()
result = rag.query("What is PrivAI?", top_k=5)
```

### Embeddings Integration
Works with the embeddings module:

```python
from app.core.embeddings import get_default_embedding_generator
from app.core.rag import RAGPipeline

# Use custom embedding generator
embedding_gen = get_default_embedding_generator()
rag = RAGPipeline(embedding_generator=embedding_gen)
```

### Vector Database Integration
Works with the vector database module:

```python
from app.core.vector_db import get_default_vector_database
from app.core.rag import RAGPipeline

# Use custom vector database
vector_db = get_default_vector_database()
rag = RAGPipeline(vector_database=vector_db)
```

## Dependencies

- `transformers`: Local LLM support
- `torch`: PyTorch for model inference
- `openai`: OpenAI API integration
- `numpy`: Vector operations
- `json`: Response serialization
- `hashlib`: Cache key generation

## Examples

See `examples/rag_examples.py` for comprehensive usage examples including:
- Basic query processing
- Advanced query capabilities
- Caching demonstration
- Model comparison
- Error handling
- Statistics and monitoring

## Troubleshooting

### Common Issues

1. **Model Loading Error**: Install transformers and torch
   ```bash
   pip install transformers torch
   ```

2. **OpenAI API Error**: Check API key and internet connection
   ```python
   rag = RAGPipeline(openai_api_key="your-key")
   ```

3. **Memory Error**: Use smaller models or reduce batch size
   ```python
   rag = RAGPipeline(local_model_name="distilgpt2")
   ```

4. **Cache Issues**: Clear cache or check permissions
   ```python
   rag.clear_cache()
   ```

### Performance Issues

1. **Slow Queries**: Enable caching and use appropriate top-k
2. **High Memory Usage**: Use smaller models or API fallback
3. **Cache Misses**: Check cache directory permissions

## Future Enhancements

- **Multi-Model Support**: Support for multiple LLM models
- **Advanced Caching**: Distributed caching and cache invalidation
- **Query Optimization**: Query rewriting and optimization
- **Response Quality**: Response quality scoring and improvement
- **Real-time Updates**: Incremental knowledge base updates

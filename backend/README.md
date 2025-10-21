# PrivAI Backend

A privacy-first FastAPI backend for college AI applications that processes documents and provides AI-powered chat functionality.

## Features

- **File Upload**: Support for PDF, CSV, and DOCX files
- **Database Connection**: Connect to various databases (PostgreSQL, MySQL, SQLite)
- **Data Ingestion**: Chunk and embed documents into FAISS vector store
- **AI Chat**: Query documents using local or cloud-based LLMs
- **Privacy-First**: All processing happens locally by default

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` with your settings (optional - defaults work for local development).

### 3. Run the Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

## API Endpoints

### File Upload
- `POST /upload/` - Upload a single file
- `POST /upload/multiple` - Upload multiple files
- `GET /upload/status/{file_id}` - Get upload status

### Database Connection
- `POST /connect-db/` - Connect to a database
- `GET /connect-db/status/{connection_id}` - Get connection status
- `DELETE /connect-db/{connection_id}` - Disconnect from database
- `GET /connect-db/` - List active connections

### Data Ingestion
- `POST /ingest/` - Ingest data from files or database
- `GET /ingest/status` - Get ingestion status
- `DELETE /ingest/clear` - Clear vector store

### AI Chat
- `POST /chat/` - Send a chat query
- `GET /chat/health` - Check chat service health
- `GET /chat/stats` - Get chat statistics

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |
| `MAX_FILE_SIZE` | `52428800` | Maximum file size in bytes |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `CHUNK_SIZE` | `1000` | Text chunk size for processing |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `LOCAL_LLM_MODEL` | `microsoft/DialoGPT-medium` | Local LLM model |
| `OPENAI_API_KEY` | `None` | OpenAI API key (optional) |
| `LOG_LEVEL` | `INFO` | Logging level |

## Architecture

```
app/
├── api/           # API endpoints
│   ├── upload.py  # File upload endpoints
│   ├── database.py # Database connection endpoints
│   ├── ingest.py  # Data ingestion endpoints
│   └── chat.py    # Chat endpoints
├── core/          # Core services
│   ├── config.py  # Configuration
│   ├── logging.py # Logging setup
│   ├── file_processor.py # File processing
│   ├── vector_store.py   # FAISS vector store
│   └── llm_service.py    # LLM integration
├── models/        # Data models
│   └── schemas.py # Pydantic models
└── main.py        # FastAPI application
```

## Usage Examples

### Upload a File

```bash
curl -X POST "http://localhost:8000/upload/" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

### Connect to Database

```bash
curl -X POST "http://localhost:8000/connect-db/" \
     -H "Content-Type: application/json" \
     -d '{"db_url": "postgresql://user:pass@localhost/dbname"}'
```

### Ingest Data

```bash
curl -X POST "http://localhost:8000/ingest/" \
     -H "Content-Type: application/json" \
     -d '{"source_type": "files", "file_ids": ["file-id-1", "file-id-2"]}'
```

### Chat Query

```bash
curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the main topic of the documents?"}'
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

## Privacy & Security

- All file processing happens locally
- No data is sent to external services unless explicitly configured
- Vector embeddings are stored locally in FAISS
- Database connections are read-only by default
- Comprehensive logging for audit trails

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **File Upload Fails**: Check file size limits and supported formats
3. **Vector Store Issues**: Ensure sufficient disk space for FAISS index
4. **LLM Errors**: Check model availability and API keys

### Logs

Application logs are written to:
- Console output
- `privai.log` file

Check logs for detailed error information.

## License

This project is part of the PrivAI application suite.

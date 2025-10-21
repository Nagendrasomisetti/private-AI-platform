# PrivAI Backend - Quick Start Guide

## 🚀 **Quick Start (Simplified Version)**

### 1. **Install Dependencies**
```bash
cd E:\Nagendra\projects\PrivAI\privai-app\backend
pip install fastapi uvicorn python-multipart pydantic-settings structlog
```

### 2. **Run the Backend**
```bash
python -m app.main_simple
```

### 3. **Access the API**
- **Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 **Test the Backend**

### **Quick Test**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is PrivAI?"}'
```

### **Run Full Test Suite**
```bash
python test_backend_simple.py
```

## 📡 **Available Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/upload/` | POST | Upload files |
| `/connect-db/` | POST | Connect to database |
| `/ingest/` | POST | Process data |
| `/chat/` | POST | AI chat |
| `/files/` | GET | List files |
| `/chunks/` | GET | List chunks |

## 🔧 **Configuration**

The simplified backend uses default settings:
- **Host**: 0.0.0.0
- **Port**: 8000
- **Debug**: True
- **Log Level**: INFO

## 📁 **File Structure**
```
backend/
├── app/
│   └── main_simple.py      # Simplified backend
├── test_backend_simple.py  # Test script
├── BACKEND_STATUS.md       # Status report
└── QUICK_START.md         # This file
```

## 🎯 **Next Steps**

1. **Test the endpoints** using the API documentation
2. **Upload sample files** to test file processing
3. **Connect to database** to test database integration
4. **Use chat interface** to test AI functionality
5. **Integrate with frontend** when ready

## 🆘 **Troubleshooting**

### **Port Already in Use**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### **Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade fastapi uvicorn python-multipart pydantic-settings structlog
```

### **Connection Refused**
- Make sure the backend is running
- Check if port 8000 is available
- Verify firewall settings

## 🎉 **Success!**

If you see the health check response, your backend is running successfully!

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 123.45
}
```

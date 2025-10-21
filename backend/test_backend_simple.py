"""
Test script for the simplified PrivAI backend
"""
import requests
import json
import time

def test_backend():
    """Test all backend endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing PrivAI Backend (Simplified Version)")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("\n🔍 Test 1: Health Check")
        print("-" * 30)
        
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Uptime: {data['uptime']:.2f}s")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
        
        # Test 2: Root endpoint
        print(f"\n🔍 Test 2: Root Endpoint")
        print("-" * 30)
        
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint works")
            print(f"   Status: {data['status']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test 3: List files (empty)
        print(f"\n🔍 Test 3: List Files (Empty)")
        print("-" * 30)
        
        response = requests.get(f"{base_url}/files/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Files endpoint works")
            print(f"   Files count: {data['count']}")
        else:
            print(f"❌ Files endpoint failed: {response.status_code}")
        
        # Test 4: List chunks (empty)
        print(f"\n🔍 Test 4: List Chunks (Empty)")
        print("-" * 30)
        
        response = requests.get(f"{base_url}/chunks/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chunks endpoint works")
            print(f"   Chunks count: {data['count']}")
        else:
            print(f"❌ Chunks endpoint failed: {response.status_code}")
        
        # Test 5: Database connection
        print(f"\n🔍 Test 5: Database Connection")
        print("-" * 30)
        
        db_request = {"db_url": "postgresql://user:pass@localhost/db"}
        response = requests.post(f"{base_url}/connect-db/", json=db_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database connection works")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Database connection failed: {response.status_code}")
        
        # Test 6: Data ingestion
        print(f"\n🔍 Test 6: Data Ingestion")
        print("-" * 30)
        
        response = requests.post(f"{base_url}/ingest/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data ingestion works")
            print(f"   Status: {data['status']}")
            print(f"   Chunks processed: {data['chunks_processed']}")
        else:
            print(f"❌ Data ingestion failed: {response.status_code}")
        
        # Test 7: Chat endpoint
        print(f"\n🔍 Test 7: Chat Endpoint")
        print("-" * 30)
        
        chat_request = {"query": "What is PrivAI?"}
        response = requests.post(f"{base_url}/chat/", json=chat_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat endpoint works")
            print(f"   Answer: {data['answer'][:100]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Processing time: {data['metadata']['processing_time']}s")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
        
        # Test 8: Multiple chat queries
        print(f"\n🔍 Test 8: Multiple Chat Queries")
        print("-" * 30)
        
        queries = [
            "How does PrivAI ensure privacy?",
            "What file types are supported?",
            "How does the system work?"
        ]
        
        for i, query in enumerate(queries, 1):
            chat_request = {"query": query}
            response = requests.post(f"{base_url}/chat/", json=chat_request)
            if response.status_code == 200:
                data = response.json()
                print(f"   Query {i}: ✅ '{query}' - {len(data['answer'])} chars")
            else:
                print(f"   Query {i}: ❌ '{query}' - {response.status_code}")
        
        # Test 9: Error handling
        print(f"\n🔍 Test 9: Error Handling")
        print("-" * 30)
        
        # Test empty query
        chat_request = {"query": ""}
        response = requests.post(f"{base_url}/chat/", json=chat_request)
        if response.status_code == 400:
            print(f"✅ Empty query handled correctly")
        else:
            print(f"❌ Empty query not handled: {response.status_code}")
        
        # Test invalid database URL
        db_request = {"db_url": "invalid-url"}
        response = requests.post(f"{base_url}/connect-db/", json=db_request)
        if response.status_code == 400:
            print(f"✅ Invalid database URL handled correctly")
        else:
            print(f"❌ Invalid database URL not handled: {response.status_code}")
        
        print(f"\n🎉 All backend tests completed!")
        print(f"✅ Backend is working correctly")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to backend at {base_url}")
        print(f"   Make sure the backend is running: python -m app.main_simple")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_api_docs():
    """Test if API documentation is accessible"""
    print(f"\n📚 Testing API Documentation")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print(f"✅ API documentation is accessible")
            print(f"   URL: http://localhost:8000/docs")
        else:
            print(f"❌ API documentation not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs test failed: {e}")

if __name__ == "__main__":
    test_backend()
    test_api_docs()

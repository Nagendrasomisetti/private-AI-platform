"""
Simple test script to verify PrivAI backend functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
            print(f"   Version: {response.json()['version']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_upload():
    """Test file upload endpoint"""
    print("\nTesting upload endpoint...")
    try:
        # Create a simple test file
        test_content = "This is a test document for PrivAI."
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = requests.post(f"{BASE_URL}/upload/", files=files)
        if response.status_code == 200:
            print("✅ Upload test passed")
            data = response.json()
            print(f"   File ID: {data['file_id']}")
            print(f"   Status: {data['status']}")
            return data['file_id']
        else:
            print(f"❌ Upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    return None

def test_ingest(file_id):
    """Test ingestion endpoint"""
    print("\nTesting ingest endpoint...")
    try:
        data = {
            "source_type": "files",
            "file_ids": [file_id],
            "chunk_size": 1000,
            "chunk_overlap": 200
        }
        
        response = requests.post(f"{BASE_URL}/ingest/", json=data)
        if response.status_code == 200:
            print("✅ Ingest test passed")
            result = response.json()
            print(f"   Chunks processed: {result['chunks_processed']}")
            print(f"   Index size: {result['index_size']}")
        else:
            print(f"❌ Ingest test failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Ingest test error: {e}")

def test_chat():
    """Test chat endpoint"""
    print("\nTesting chat endpoint...")
    try:
        data = {
            "query": "What is this document about?",
            "top_k": 3,
            "use_local_llm": True
        }
        
        response = requests.post(f"{BASE_URL}/chat/", json=data)
        if response.status_code == 200:
            print("✅ Chat test passed")
            result = response.json()
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Model used: {result['model_used']}")
            print(f"   Sources: {len(result['sources'])}")
        else:
            print(f"❌ Chat test failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat test error: {e}")

def main():
    """Run all tests"""
    print("🚀 PrivAI Backend Test Suite")
    print("=" * 40)
    
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Run tests
    test_health()
    file_id = test_upload()
    
    if file_id:
        test_ingest(file_id)
        test_chat()
    
    print("\n" + "=" * 40)
    print("✅ Test suite completed!")

if __name__ == "__main__":
    main()

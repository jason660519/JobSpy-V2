#!/usr/bin/env python3
"""
Quick test script for JobSpy v2 API
"""
import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing JobSpy v2 API")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
        return
    
    # Test 2: Root endpoint
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Root endpoint: PASSED")
            print(f"   Message: {response.json()['message']}")
        else:
            print(f"❌ Root endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Root endpoint: ERROR - {e}")
    
    # Test 3: Job search (GET)
    try:
        search_params = {
            "query": "software engineer",
            "location": "taipei",
            "job_type": "full-time"
        }
        response = requests.get(f"{base_url}/api/v1/jobs/search", params=search_params)
        if response.status_code == 200:
            data = response.json()
            print("✅ Job search (GET): PASSED")
            print(f"   Found {data['total_count']} jobs")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Job search (GET): FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Job search (GET): ERROR - {e}")
    
    # Test 4: Job search (POST)
    try:
        search_data = {
            "query": "python developer",
            "location": "remote",
            "job_type": "full-time"
        }
        response = requests.post(f"{base_url}/api/v1/jobs/search", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Job search (POST): PASSED")
            print(f"   Found {data['total_count']} jobs")
            if data['jobs']:
                first_job = data['jobs'][0]
                print(f"   Sample job: {first_job['title']} at {first_job['company']}")
        else:
            print(f"❌ Job search (POST): FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Job search (POST): ERROR - {e}")
    
    print("\n🎉 API Testing Complete!")
    print(f"📖 View full API docs at: {base_url}/docs")

if __name__ == "__main__":
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    test_api()
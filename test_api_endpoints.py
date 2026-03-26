import requests
import json

# Test all API endpoints to see if they return JSON
api_urls = [
    "http://localhost:5001/api",
    "http://localhost:5001/api/login",
    "http://localhost:5001/api/register",
    "http://localhost:5001/api/user"
]

for url in api_urls:
    print(f"\nTesting {url}...")
    try:
        # Test GET requests
        print("  GET request:")
        response = requests.get(url)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content snippet: {response.text[:100]}...")
    except Exception as e:
        print(f"  GET error: {e}")
    
    # Test POST for login/register
    if '/login' in url or '/register' in url:
        try:
            print("  POST request:")
            payload = {
                "identifier": "test@example.com",
                "password": "test123",
                "agree_to_terms": True
            }
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            print(f"  Content snippet: {response.text[:100]}...")
        except Exception as e:
            print(f"  POST error: {e}")
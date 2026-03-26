import requests
import json

# Test the local API endpoints
base_url = "http://localhost:5001"

def test_endpoint(url, method="GET", data=None):
    print(f"\nTesting {url} ({method})...")
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content: {response.text}")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"JSON parsed successfully")
        except json.JSONDecodeError:
            print(f"ERROR: Could not parse as JSON")
            
    except Exception as e:
        print(f"Error: {e}")

# Test cases
print("Testing local API endpoints...")

test_endpoint(f"{base_url}/api/login", method="POST", data={
    "identifier": "test@example.com",
    "password": "test123",
    "agree_to_terms": True
})

test_endpoint(f"{base_url}/api/user")

test_endpoint(f"{base_url}/")

test_endpoint(f"{base_url}/not-found")
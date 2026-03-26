import requests
import json

# Test the login and register endpoints
print("Testing API endpoints...")

def test_endpoint(name, url, method="POST", data=None, expected_status=200):
    print(f"\nTesting {name}...")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Data: {data}")
    
    try:
        headers = {"Content-Type": "application/json"}
        if method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.get(url)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content: {response.text}")
        
        if response.status_code == expected_status:
            print(f"✅ {name} test passed!")
        else:
            print(f"❌ {name} test failed! Expected {expected_status}, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ {name} test failed with error: {e}")

# Test data
register_data = {
    "email": "test_new@example.com",
    "username": "testuser",
    "password": "test123456",
    "agree_to_terms": True
}

login_data = {
    "identifier": "test_new@example.com",
    "password": "test123456",
    "agree_to_terms": True
}

# Test endpoints
base_url = "http://localhost:5001/api"
test_endpoint("Register", f"{base_url}/register", data=register_data)
test_endpoint("Login", f"{base_url}/login", data=login_data)
test_endpoint("Login with invalid credentials", f"{base_url}/login", data={"identifier": "invalid", "password": "invalid"}, expected_status=401)

test_endpoint("Register with missing data", f"{base_url}/register", data={"email": "test@example.com"}, expected_status=400)

test_endpoint("Register with short password", f"{base_url}/register", data={"email": "test@example.com", "username": "test", "password": "123"}, expected_status=400)

test_endpoint("Login with missing data", f"{base_url}/login", data={"identifier": "test@example.com"}, expected_status=400)

test_endpoint("Login with None data", f"{base_url}/login", data=None, expected_status=400)

test_endpoint("Login with empty data", f"{base_url}/login", data={}, expected_status=400)

print("\nAll tests completed!")
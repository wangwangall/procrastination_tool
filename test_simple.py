import requests
import json

print("Testing API endpoints...\n")

# Test data
register_data = {
    "email": "test2@example.com",
    "username": "testuser2",
    "password": "test123456",
    "agree_to_terms": True
}

login_data = {
    "identifier": "test2@example.com",
    "password": "test123456",
    "agree_to_terms": True
}

# Test endpoints
base_url = "http://localhost:5001/api"

# Test register
print("1. Testing Register endpoint...")
response = requests.post(f"{base_url}/register", headers={"Content-Type": "application/json"}, json=register_data)
print(f"   Status: {response.status_code}")
print(f"   Content-Type: {response.headers.get('Content-Type')}")
print(f"   Response: {response.text[:150]}...")

# Test login
print("\n2. Testing Login endpoint...")
response = requests.post(f"{base_url}/login", headers={"Content-Type": "application/json"}, json=login_data)
print(f"   Status: {response.status_code}")
print(f"   Content-Type: {response.headers.get('Content-Type')}")
print(f"   Response: {response.text[:150]}...")

# Test invalid login
print("\n3. Testing Login with invalid credentials...")
response = requests.post(f"{base_url}/login", headers={"Content-Type": "application/json"}, json={"identifier": "invalid", "password": "invalid"})
print(f"   Status: {response.status_code}")
print(f"   Content-Type: {response.headers.get('Content-Type')}")
print(f"   Response: {response.text[:150]}...")

# Test missing data
print("\n4. Testing Login with missing data...")
response = requests.post(f"{base_url}/login", headers={"Content-Type": "application/json"}, json={"identifier": "test@example.com"})
print(f"   Status: {response.status_code}")
print(f"   Content-Type: {response.headers.get('Content-Type')}")
print(f"   Response: {response.text[:150]}...")

print("\nAll tests completed!")
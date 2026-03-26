import requests
import json

# Test the login endpoint
url = "http://localhost:5001/api/login"
payload = {
    "identifier": "test@example.com",
    "password": "test123",
    "agree_to_terms": True
}

headers = {
    "Content-Type": "application/json"
}

print("Testing login endpoint...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Content: {response.text}")
except Exception as e:
    print(f"Error: {e}")
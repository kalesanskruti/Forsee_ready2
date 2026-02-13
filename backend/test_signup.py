import requests
import json

url = "http://127.0.0.1:8001/api/v1/users/"
payload = {
    "email": "test_script@example.com",
    "password": "longerpassword123",
    "full_name": "Test Script User"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")

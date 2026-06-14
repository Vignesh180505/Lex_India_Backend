import requests
import json

url = "http://127.0.0.1:8000/api/query"
payload = {
    "issue": "I want to file a case about copyright infringement of my software source code in court.",
    "language": "en"
}
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending POST request to {url}...")
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request failed: {e}")

import requests
import json

url = "http://localhost:8000/api/query"
payload = {
    "issue": "I want to know about gender equality and protection for women from domestic violence.",
    "language": "en"
}
headers = {"Content-Type": "application/json"}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Success! First law found:")
        if data['laws']:
            law = data['laws'][0]
            print(f"  Act: {law['act_name']}")
            print(f"  Section: {law['section_number']}")
            print(f"  Punishment: {law.get('punishment')}")
        else:
            print("  No laws returned.")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")

import asyncio
import httpx
import json

async def test_search():
    url = "http://127.0.0.1:8000/api/judgments/search"
    payload = {
        "query": "tenant eviction",
        "mode": "citizen",
        "page": 0
    }
    
    print(f"Testing search API at {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {data.get('total_found')} judgments.")
                print(f"First result: {data.get('judgments', [{}])[0].get('title', 'N/A')}")
            else:
                print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())

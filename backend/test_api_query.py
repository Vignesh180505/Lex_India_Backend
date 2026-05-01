"""Test API query - writes results to a file."""
import requests
import json

resp = requests.post(
    'http://localhost:8000/api/query',
    json={'issue': 'bus conductor did not give me change', 'language': 'en'},
    timeout=300
)

data = resp.json()

with open('test_result.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)

print(f"Status: {resp.status_code}")
print(f"Laws count: {len(data.get('laws', []))}")

scores = []
for law in data.get('laws', []):
    s = law.get('relevance_score', 0)
    scores.append(s)
    print(f"  {law.get('section_id')}: score={s}, severity={law.get('severity')}")

if scores and all(s == 0.50 for s in scores):
    print("BUG: All 0.50")
elif scores:
    print(f"OK: min={min(scores)}, max={max(scores)}")
else:
    print("No laws returned")

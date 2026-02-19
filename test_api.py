import requests
import json

response = requests.post(
    'http://localhost:5001/api/analyze',
    json={
        'keywords': 'python',
        'subreddits': 'python',
        'limit': 2,
        'sort': 'hot'
    }
)

print(json.dumps(response.json(), indent=2))
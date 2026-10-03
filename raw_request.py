import json
import os
 
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1") + "/chat/completions"
 
headers = {
    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
    "Content-Type": "application/json",
}
 
body = {
    "model": os.environ["LLM_MODEL"],
    "messages": [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Explain what a REST API is in one sentence."},
    ],
    "temperature": 0.2,
}
 
response = requests.post(url, headers=headers, json=body, timeout=30)
 
print("Status code:", response.status_code)
data = response.json()                      # JSON text -> Python dict
print(json.dumps(data, indent=2))           # pretty-print the whole response
print("\nJust the reply:", data["choices"][0]["message"]["content"])
print("Tokens used:", data["usage"]["total_tokens"])
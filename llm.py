import os
import time
 
from dotenv import load_dotenv
from openai import OpenAI
 
load_dotenv()
 
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("LLM_MODEL")
API_KEY = os.getenv("GROQ_API_KEY")
 
if not API_KEY or not MODEL:
    raise RuntimeError("Set GROQ_API_KEY and LLM_MODEL in your .env file")
 
client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=60, max_retries=2)
 
 
def chat(messages, temperature=0.2, **kwargs):
    """Send a list of messages. Returns (reply_text, usage_dict, latency_seconds)."""
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )
    latency = time.perf_counter() - start
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "total_tokens": resp.usage.total_tokens,
    }
    return resp.choices[0].message.content, usage, round(latency, 2)
 
 
if __name__ == "__main__":
    reply, usage, latency = chat([
        {"role": "system", "content": "You are a concise Python expert."},
        {"role": "user", "content": "Write a Python function that reverses a string."},
    ])
    print(reply)
    print(f"\nTokens: {usage}  |  Latency: {latency}s")
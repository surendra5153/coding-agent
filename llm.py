"""Thin wrapper around an OpenAI-compatible chat completions API."""
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
 
 
def _usage(resp):
    """Pull token counts out of a response as a plain dict."""
    return {
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "total_tokens": resp.usage.total_tokens,
    }
 
 
def chat(messages, temperature=0.2, **kwargs):
    """Send messages. Returns (reply_text, usage_dict, latency_seconds)."""
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, temperature=temperature, **kwargs
    )
    latency = round(time.perf_counter() - start, 2)
    return resp.choices[0].message.content, _usage(resp), latency
 
 
def chat_with_tools(messages, tools, temperature=0.2, tool_choice="auto"):
    """Like chat(), but returns the full message so tool calls are visible.
 
    Returns (message, usage_dict, latency_seconds). message.content may be None
    and message.tool_calls may be a list of requested tool calls.
    """
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
    )
    latency = round(time.perf_counter() - start, 2)
    return resp.choices[0].message, _usage(resp), latency
 
 
if __name__ == "__main__":
    reply, usage, latency = chat([
        {"role": "system", "content": "You are a concise Python expert."},
        {"role": "user", "content": "Write a Python function that reverses a string."},
    ])
    print(reply)
    print(f"\nTokens: {usage}  |  Latency: {latency}s")
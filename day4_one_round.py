"""Day 4: one complete tool-calling round trip, printed step by step."""
import json
 
from llm import chat_with_tools
from tools import TOOLS, assistant_message_to_dict, execute_tool_call, tool_message
 
messages = [
    {"role": "system", "content": "You are a Python coding assistant. Always test your code by calling run_code."},
    {"role": "user", "content": (
        "Write a function is_palindrome(s) that ignores case and non-letter characters. "
        "Test it with a few asserts and print the results."
    )},
]
 
# ---- CALL 1: send the task plus the tool list ----
print("=== CALL 1: task + tools ===")
msg, usage, latency = chat_with_tools(messages, TOOLS)
print(f"tool calls requested: {len(msg.tool_calls or [])} | tokens: {usage['total_tokens']} | {latency}s")
 
if not msg.tool_calls:
    print("The model answered with text instead of calling the tool:\n", msg.content)
    raise SystemExit(0)
 
messages.append(assistant_message_to_dict(msg))     # must come BEFORE the tool messages
 
for tc in msg.tool_calls:
    print(f"\nModel requested '{tc.function.name}' (id={tc.id})")
    print("Raw arguments (a JSON *string*), first 400 chars:")
    print(tc.function.arguments[:400])
 
    result, code = execute_tool_call(tc)
    print("\nSandbox result:")
    print(json.dumps(result, indent=2)[:800])
    messages.append(tool_message(tc, result))       # answer this specific call id
 
# ---- CALL 2: send everything back so the model can see the result ----
print("\n=== CALL 2: history + tool result ===")
msg2, usage2, latency2 = chat_with_tools(messages, TOOLS)
if msg2.tool_calls:
    print("The model wants to run code again (it found a problem). Day 5's loop handles this.")
else:
    print("Model's final reply:\n", msg2.content)
 
print("\n=== The conversation, as roles ===")
for m in messages:
    extra = f" ({len(m['tool_calls'])} tool call)" if m.get("tool_calls") else ""
    print(f"- {m['role']}{extra}")
print("- assistant (call 2 reply)")
print(f"Prompt tokens grew from {usage['prompt_tokens']} to {usage2['prompt_tokens']}")

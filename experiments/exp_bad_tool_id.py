import openai
 
from llm import chat_with_tools
from tools import TOOLS, assistant_message_to_dict, execute_tool_call, tool_message
 
messages = [{"role": "user", "content": "Write and run code that prints 2 + 2."}]
msg, _, _ = chat_with_tools(messages, TOOLS, tool_choice="required")
tc = msg.tool_calls[0]
result, _ = execute_tool_call(tc)
 
# Mistake A: append the tool result WITHOUT the assistant message first
try:
    chat_with_tools(messages + [tool_message(tc, result)], TOOLS)
except openai.BadRequestError as e:
    print("Mistake A rejected:", e.status_code)
 
# Mistake B: correct order, but a wrong tool_call_id
bad = tool_message(tc, result)
bad["tool_call_id"] = "call_does_not_exist"
try:
    chat_with_tools(messages + [assistant_message_to_dict(msg), bad], TOOLS)
except openai.BadRequestError as e:
    print("Mistake B rejected:", e.status_code)
 
# Correct version works
ok, _, _ = chat_with_tools(messages + [assistant_message_to_dict(msg), tool_message(tc, result)], TOOLS)
print("Correct version accepted. Reply:", (ok.content or "")[:80])

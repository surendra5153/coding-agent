from llm import chat_with_tools
from tools import TOOLS, assistant_message_to_dict, execute_tool_call, tool_message
 
messages = [
    {"role": "system", "content": "Always test code with run_code. If it fails, fix it and run it again."},
    {"role": "user", "content": "Write average(nums) returning the mean of a list. "
                                "Your test MUST include average([]) and it must return 0 for an empty list."},
]
 
for turn in range(1, 4):
    msg, _, _ = chat_with_tools(messages, TOOLS)
    if not msg.tool_calls:
        print(f"turn {turn}: final text -> {(msg.content or '')[:100]}")
        break
    messages.append(assistant_message_to_dict(msg))
    for tc in msg.tool_calls:
        result, _ = execute_tool_call(tc)
        last = (result.get("stderr") or "").strip().splitlines()[-1:] or ["(no stderr)"]
        print(f"turn {turn}: status={result['status']}  {last[0][:80]}")
        messages.append(tool_message(tc, result))

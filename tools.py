"""Tool definitions the LLM can call, and the code that executes them safely."""
import json
 
from sandbox import run_in_sandbox
 
# ---------- Part 1: the tool description the model reads ----------
RUN_CODE_TOOL = {
    "type": "function",
    "function": {
        "name": "run_code",
        "description": (
            "Run a complete, self-contained Python 3.12 program in an isolated sandbox. "
            "No network access, 256 MB memory, a time limit of a few seconds, standard "
            "library only. Returns JSON with: status (ok, error, timeout, oom, infra_error), "
            "exit_code, stdout, stderr, duration_s."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The full Python source code. It is saved and run as main.py.",
                }
            },
            "required": ["code"],
        },
    },
}
 
TOOLS = [RUN_CODE_TOOL]
 
# ---------- Part 2: extra guidance for special failure types ----------
HINTS = {
    "timeout": "The program exceeded the time limit. Look for an infinite loop or an algorithm that is too slow.",
    "oom": "The program was killed for using too much memory (limit 256 MB). Use less memory.",
    "infra_error": "The sandbox itself failed. This is not a problem with your code.",
}
 
 
# ---------- Part 3: run one tool call safely ----------
def execute_tool_call(tool_call, timeout=10):
    """Execute one tool call requested by the model.
 
    Returns (result_dict, code). code is None if the arguments were unusable.
    Never raises: every problem becomes a result the model can read.
    """
    name = tool_call.function.name
    if name != "run_code":
        return {"status": "error", "error": f"Unknown tool '{name}'. The only tool is run_code."}, None
 
    try:
        args = json.loads(tool_call.function.arguments or "{}")
        code = args["code"]
        if not isinstance(code, str) or not code.strip():
            raise ValueError("'code' must be a non-empty string")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        return {
            "status": "error",
            "error": f"Invalid arguments for run_code: {e}. "
                     "Call run_code again with a JSON object like {\"code\": \"...\"}.",
        }, None
 
    result = run_in_sandbox(code, timeout=timeout).to_dict()
    if result["status"] in HINTS:
        result["hint"] = HINTS[result["status"]]
    return result, code
 
 
# ---------- Part 4: build correctly-shaped messages ----------
def tool_message(tool_call, result):
    """The message that returns a tool result to the model."""
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    }
 
 
def assistant_message_to_dict(msg):
    """Convert the SDK's message object into a plain dict we can append to history."""
    d = {"role": "assistant", "content": msg.content or ""}
    if msg.tool_calls:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in msg.tool_calls
        ]
    return d

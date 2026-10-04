"""Tests for tools.py using fake tool-call objects (no LLM calls)."""
import json
from types import SimpleNamespace
 
from tools import assistant_message_to_dict, execute_tool_call, tool_message
 
 
def fake_call(arguments, name="run_code", call_id="call_1"):
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))
 
 
def test_valid_call_runs_code():
    result, code = execute_tool_call(fake_call(json.dumps({"code": "print(6 * 7)"})))
    assert result["status"] == "ok"
    assert "42" in result["stdout"]
    assert code == "print(6 * 7)"
 
 
def test_malformed_json_is_reported_not_raised():
    result, code = execute_tool_call(fake_call('{"code": "print(1)"'))   # missing closing brace
    assert result["status"] == "error"
    assert "Invalid arguments" in result["error"]
    assert code is None
 
 
def test_missing_code_key():
    result, code = execute_tool_call(fake_call(json.dumps({"source": "print(1)"})))
    assert result["status"] == "error"
    assert code is None
 
 
def test_unknown_tool_name():
    result, code = execute_tool_call(fake_call("{}", name="delete_files"))
    assert "Unknown tool" in result["error"]
    assert code is None
 
 
def test_timeout_gets_a_hint():
    call = fake_call(json.dumps({"code": "while True:\n    pass"}))
    result, _ = execute_tool_call(call, timeout=2)
    assert result["status"] == "timeout"
    assert "infinite loop" in result["hint"]
 
 
def test_tool_message_shape():
    msg = tool_message(fake_call("{}"), {"status": "ok"})
    assert msg["role"] == "tool"
    assert msg["tool_call_id"] == "call_1"
    assert json.loads(msg["content"]) == {"status": "ok"}
 
 
def test_assistant_message_keeps_tool_calls():
    sdk_msg = SimpleNamespace(content=None, tool_calls=[fake_call('{"code": "x"}')])
    d = assistant_message_to_dict(sdk_msg)
    assert d["role"] == "assistant"
    assert d["content"] == ""
    assert d["tool_calls"][0]["id"] == "call_1"
    assert d["tool_calls"][0]["type"] == "function"
    assert d["tool_calls"][0]["function"]["name"] == "run_code"

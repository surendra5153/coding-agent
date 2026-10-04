"""Tests that prove run_in_sandbox() meets its spec."""
from sandbox import LABEL, get_client, run_in_sandbox
 
 
def test_hello_world():
    r = run_in_sandbox('print("hello from the sandbox")')
    assert r.status == "ok"
    assert r.exit_code == 0
    assert "hello from the sandbox" in r.stdout
 
 
def test_runtime_error_is_captured_not_raised():
    r = run_in_sandbox("x = 1 / 0")
    assert r.status == "error"
    assert r.exit_code == 1
    assert "ZeroDivisionError" in r.stderr
 
 
def test_syntax_error_is_captured():
    r = run_in_sandbox("def broken(:\n    pass")
    assert r.status == "error"
    assert "SyntaxError" in r.stderr
 
 
def test_infinite_loop_times_out():
    r = run_in_sandbox("while True:\n    pass", timeout=3)
    assert r.status == "timeout"
    assert r.timed_out is True
    assert r.duration_s < 10
 
 
def test_network_is_blocked():
    code = (
        "import urllib.request\n"
        "urllib.request.urlopen('http://example.com', timeout=3)\n"
    )
    r = run_in_sandbox(code)
    assert r.status == "error"
    assert "URLError" in r.stderr or "Errno" in r.stderr
 
 
def test_memory_limit_kills_process():
    code = (
        "chunks = []\n"
        "for _ in range(40):\n"
        "    chunks.append(b'x' * 50_000_000)\n"
    )
    r = run_in_sandbox(code, timeout=20)
    assert r.status == "oom"
    assert r.oom_killed is True
 
 
def test_workspace_is_read_only():
    r = run_in_sandbox("open('/workspace/hacked.txt', 'w').write('x')")
    assert r.status == "error"
    assert "Read-only file system" in r.stderr or "Permission denied" in r.stderr
 
 
def test_tmp_is_writable():
    code = "open('/tmp/ok.txt', 'w').write('hi')\nprint(open('/tmp/ok.txt').read())"
    r = run_in_sandbox(code)
    assert r.status == "ok"
    assert "hi" in r.stdout
 
 
def test_large_output_is_truncated():
    r = run_in_sandbox("print('A' * 100_000)")
    assert r.status == "ok"
    assert "characters truncated" in r.stdout
    assert len(r.stdout) < 5000
 
 
def test_unicode_output_survives():
    r = run_in_sandbox("print('namaste: \u0928\u092e\u0938\u094d\u0924\u0947 \u2713')")
    assert r.status == "ok"
    assert "\u0928\u092e\u0938\u094d\u0924\u0947" in r.stdout
 
 
def test_no_containers_left_behind():
    run_in_sandbox("print('cleanup check')")
    run_in_sandbox("while True:\n    pass", timeout=2)
    label_filter = f"app={LABEL['app']}"
    leftovers = get_client().containers.list(all=True, filters={"label": label_filter})
    assert leftovers == []

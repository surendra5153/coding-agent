"""Human-readable demo of run_in_sandbox()."""
from sandbox import run_in_sandbox
 
SNIPPETS = {
    "hello": 'print("hi from the sandbox")',
    "crash": "print(undefined_variable)",
    "loop": "while True:\n    pass",
}
 
for name, code in SNIPPETS.items():
    r = run_in_sandbox(code, timeout=3)
    print(f"--- {name} ---")
    print(f"status={r.status}  exit={r.exit_code}  time={r.duration_s}s")
    if r.stdout:
        print("stdout:", r.stdout.strip())
    if r.stderr:
        print("last stderr line:", r.stderr.strip().splitlines()[-1])
    print()

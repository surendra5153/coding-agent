"""How much time does the sandbox itself add to each run?"""
import statistics
 
from sandbox import run_in_sandbox
 
times = [run_in_sandbox("pass").duration_s for _ in range(10)]
 
print("Runs:", times)
print(f"min={min(times)}s  median={statistics.median(times)}s  max={max(times)}s")

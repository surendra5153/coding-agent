"""Run untrusted Python code inside a locked-down Docker container."""
import os
import tempfile
import time
from dataclasses import dataclass, asdict
 
import docker
from docker.errors import APIError, DockerException
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout
 
IMAGE = "agent-sandbox"
LABEL = {"app": "coding-agent-sandbox"}
MAX_OUTPUT_CHARS = 4000
DIR_PERMISSIONS = 0o755            # dir permissions: owner rwx, everyone else r-x
SCRIPT_PERMISSIONS = 0o644         # file permissions: owner rw, everyone else r--

_client = None
 
 
def get_client():
    """Create the Docker client once and reuse it for every run."""
    global _client
    if _client is None:
        _client = docker.from_env()
        _client.ping()          # fail fast if the daemon is not reachable
    return _client

@dataclass
class SandboxResult:
    status: str          # "ok" | "error" | "timeout" | "oom" | "infra_error"
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    oom_killed: bool
    duration_s: float
 
    def to_dict(self):
        """Plain dict version, ready for JSON (used for logging and for the LLM)."""
        return asdict(self)

def _truncate(text, limit=MAX_OUTPUT_CHARS):
    """Keep the start and (mostly) the end of long output; errors are usually at the end."""
    if len(text) <= limit:
        return text
    head = limit // 4
    tail = limit - head
    cut = len(text) - limit
    return f"{text[:head]}\n...[{cut} characters truncated]...\n{text[-tail:]}"
 
 
def _classify(exit_code, timed_out, oom_killed):
    """Map raw facts to one status category. Order matters: timeout first."""
    if timed_out:
        return "timeout"
    if oom_killed:
        return "oom"
    return "ok" if exit_code == 0 else "error"

def run_in_sandbox(code: str, timeout: int = 10) -> SandboxResult:
    """Execute code as main.py in an isolated container and report what happened."""
    start = time.perf_counter()
    container = None
 
    with tempfile.TemporaryDirectory(prefix="sandbox_") as workdir:
        # 1. Write the code to a fresh, private folder
        script_path = os.path.join(workdir, "main.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
 
        # 2. The container runs as uid 10001, not as you: give it read access
        os.chmod(workdir, DIR_PERMISSIONS)
        os.chmod(script_path, SCRIPT_PERMISSIONS)
 
        try:
            # 3. Start the container in the background with every restriction
            container = get_client().containers.run(
                IMAGE,
                ["python", "main.py"],
                detach=True,
                labels=LABEL,
                working_dir="/workspace",
                volumes={workdir: {"bind": "/workspace", "mode": "ro"}},
                network_mode="none",
                mem_limit="256m",
                memswap_limit="256m",
                nano_cpus=500_000_000,          # 0.5 CPU (1 CPU = 1e9 nano-CPUs)
                pids_limit=64,
                read_only=True,
                tmpfs={"/tmp": "rw,size=16m"},
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
            )
 
            # 4. Wait with a deadline; on timeout, SIGKILL it ourselves
            timed_out = False
            try:
                exit_code = container.wait(timeout=timeout)["StatusCode"]
            except (ReadTimeout, RequestsConnectionError):
                timed_out = True
                exit_code = -1
                try:
                    container.kill()
                except APIError:
                    pass  # it finished at the exact moment we gave up; that's fine
 
            # 5. Gather facts: refresh state, detect OOM, read both streams
            container.reload()
            oom_flag = bool(container.attrs["State"].get("OOMKilled", False))
            oom_killed = oom_flag or (exit_code == 137 and not timed_out)
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
 
            return SandboxResult(
                status=_classify(exit_code, timed_out, oom_killed),
                exit_code=exit_code,
                stdout=_truncate(stdout),
                stderr=_truncate(stderr),
                timed_out=timed_out,
                oom_killed=oom_killed,
                duration_s=round(time.perf_counter() - start, 2),
            )
 
        except DockerException as e:
            # 6. Docker itself failed: report it, never crash the caller
            return SandboxResult(
                status="infra_error",
                exit_code=-1,
                stdout="",
                stderr=f"Sandbox infrastructure error: {e}",
                timed_out=False,
                oom_killed=False,
                duration_s=round(time.perf_counter() - start, 2),
            )
 
        finally:
            # 7. Always remove the container, whatever happened above
            if container is not None:
                try:
                    container.remove(force=True)
                except DockerException:
                    pass

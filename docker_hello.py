"""First contact with the Docker SDK."""
import docker
 
client = docker.from_env()                       # connect to the local daemon
print("Daemon reachable:", client.ping())        # True if it answered
print("Server version:", client.version()["Version"])
 
# Blocking run: waits for the container to finish and returns its output as bytes
output = client.containers.run(
    "agent-sandbox",
    ["python", "-c", "print(2 + 2)"],
    remove=True,                                 # same as --rm
)
print("Output:", output.decode().strip())
 
# What happens when the code fails?
try:
    client.containers.run("agent-sandbox", ["python", "-c", "1/0"], remove=True)
except docker.errors.ContainerError as e:
    print("ContainerError, exit status:", e.exit_status)
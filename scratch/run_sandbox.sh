#!/usr/bin/env bash
# Usage: ./run_sandbox.sh SCRIPT.py [extra docker flags...]
# Runs SCRIPT.py from the current folder inside the locked-down sandbox.
set -euo pipefail
 
SCRIPT="$1"
shift            # remove the script name; anything left is extra docker flags
 
# 'exec' replaces this shell with docker, so signals go straight to docker
exec docker run --rm \
  --network none \
  --memory 256m --memory-swap 256m \
  --cpus 0.5 \
  --pids-limit 64 \
  --read-only --tmpfs /tmp:rw,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -v "$(pwd):/workspace:ro" \
  "$@" \
  agent-sandbox python "$SCRIPT"
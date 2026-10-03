# Small official Python image. Pinning the minor version means every run
# uses the same interpreter, today and six months from now.
FROM python:3.12-slim
 
# PYTHONDONTWRITEBYTECODE: don't try to write .pyc files (the workspace is read-only)
# PYTHONUNBUFFERED: print output immediately, so nothing is lost if we kill the process
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
 
# Pre-install pytest now; on Day 8 the agent's code is tested inside this image.
# --no-cache-dir keeps the image smaller.
RUN pip install --no-cache-dir pytest==8.3.3
 
# Create an unprivileged user with a fixed, unusual UID and switch to it.
RUN useradd --create-home --uid 10001 runner
USER runner
 
# Default working directory; the agent's code will be mounted here.
WORKDIR /workspace


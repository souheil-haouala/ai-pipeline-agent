# --- Stage 1: Build & Dependency Collection ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing byte code (.pyc) to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Force streams to flash immediately to terminal logs
ENV PYTHONUNBUFFERED=1

# Install baseline OS system requirements if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests and pull wheels into a isolated directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Minimal Production Runtime ---
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Inform the container environment where our python path resides
ENV PATH=/root/.local/bin:$PATH

# Safely copy compiled user dependencies from the builder layer
COPY --from=builder /root/.local /root/.local

# Copy application backend codebase elements
COPY main.py detector.py agent-config.yaml ./

# Create a placeholder empty .env file so the application doesn't crash on boot 
# Environment variables should be injected securely at runtime instead
RUN touch .env

# Set the default boot command for container deployments
ENTRYPOINT ["python", "main.py"]

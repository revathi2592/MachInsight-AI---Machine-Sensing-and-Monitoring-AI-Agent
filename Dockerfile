FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y curl unzip ca-certificates git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies and ADK CLI
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install vertexai-agent-sdk

# Copy your project code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Run the ADK agent UI
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]

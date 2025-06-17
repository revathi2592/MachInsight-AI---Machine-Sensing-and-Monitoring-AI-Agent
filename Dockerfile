FROM python:3.11-slim

# Set work directory
WORKDIR /app

# System dependencies needed for pip + ADK CLI
RUN apt-get update && apt-get install -y curl unzip && apt-get clean

# Install ADK CLI
RUN curl -LO https://storage.googleapis.com/vertex-agent-sdk/google-cloud-agent-sdk-cli.zip && \
    unzip google-cloud-agent-sdk-cli.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/adk && \
    rm google-cloud-agent-sdk-cli.zip

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Environment settings
ENV PYTHONUNBUFFERED=1

# Cloud Run listens on port 8080
EXPOSE 8080

# Start the agent using ADK
CMD ["adk", "web"]

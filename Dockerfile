FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl unzip && apt-get clean

# Download and install the ADK CLI
RUN curl -LO https://storage.googleapis.com/vertex-ai-agent-sdk/google-cloud-agent-sdk-cli.zip && \
    unzip google-cloud-agent-sdk-cli.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/adk && \
    rm google-cloud-agent-sdk-cli.zip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Cloud Run settings
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Start the ADK agent
CMD ["adk", "web"]

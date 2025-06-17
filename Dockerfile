FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git curl unzip gcc && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install Google ADK CLI from GitHub
RUN git clone https://github.com/GoogleCloudPlatform/vertex-ai-agent-sdk /adk && \
    pip install /adk/cli

# Copy project files
COPY . .

# Cloud Run port and env settings
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Start the agent
CMD ["adk", "web"]

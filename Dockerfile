FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl unzip && apt-get clean

# Download and install the ADK CLI
RUN apt-get update && apt-get install -y curl unzip && \
    curl -sSL https://google.github.io/adk/install.sh | bash

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

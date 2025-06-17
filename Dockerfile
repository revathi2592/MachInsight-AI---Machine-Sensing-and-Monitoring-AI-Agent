FROM python:3.11-slim

# Set working directory
WORKDIR /app

# System dependencies needed for pip and wheel
RUN apt-get update && apt-get install -y gcc curl unzip && apt-get clean

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install the ADK CLI from PyPI
RUN pip install google-cloud-agent-sdk-cli

# Copy the rest of the application code
COPY . .

# Environment setup
ENV PYTHONUNBUFFERED=1

# Expose the port Cloud Run expects
EXPOSE 8080

# Start your agent
CMD ["adk", "web"]

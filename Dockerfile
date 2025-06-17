FROM python:3.11-slim

# Set work directory
WORKDIR /app


# Install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y curl unzip ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
 

 

# Install Python dependencies including ADK
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install google-adk

# Copy source code
COPY . .

# Cloud Run settings
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Start the ADK agent
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]


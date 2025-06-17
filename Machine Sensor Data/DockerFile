# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to cache Docker layer
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Set environment variables (Cloud Run will set .env via settings)
ENV PYTHONUNBUFFERED=1

# Expose port (Cloud Run uses the PORT environment variable)
EXPOSE 8080

# Command to run the agent using ADK
CMD ["adk", "web"]

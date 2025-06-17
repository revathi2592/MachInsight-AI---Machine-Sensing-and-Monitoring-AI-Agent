FROM python:3.11-slim

#WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl ca-certificates git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install google-adk

COPY . .

# Set working directory to the folder containing agent.py
WORKDIR /app/machine_sensor_data/sensor_agent

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

#CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
#CMD ["python", "-m", "machine_sensor_data.sensor_agent.agent"]
CMD ["sh", "-c", "adk web --host 0.0.0.0 --port ${PORT:-8080}"]

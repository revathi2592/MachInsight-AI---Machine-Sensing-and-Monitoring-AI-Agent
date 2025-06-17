FROM python:3.11-slim

WORKDIR /app
#WORKDIR /app/machine_sensor_data

RUN apt-get update && \
    apt-get install -y curl ca-certificates git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
      google-cloud-aiplatform[agent_engines,adk] \
      -r requirements.txt
#RUN which adk && adk --version
#RUN adk --version


COPY . .

# Set working directory to the folder containing agent.py
#WORKDIR /app/machine_sensor_data/sensor_agent
#WORKDIR /app/machine_sensor_data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/machine_sensor_data:$PYTHONPATH

EXPOSE 8080

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
#CMD ["python", "-m", "machine_sensor_data.sensor_agent.agent"]
#CMD ["sh", "-c", "adk web --host 0.0.0.0 --port ${PORT:-8080}"]
#CMD ["sh", "-c", "env && adk web --host 0.0.0.0 --port $PORT"]
#CMD ["python", "-m", "machine_sensor_data.sensor_agent.agent"]
#CMD ["python", "-m", "adk", "web", "--host", "0.0.0.0", "--port", "${PORT}"]



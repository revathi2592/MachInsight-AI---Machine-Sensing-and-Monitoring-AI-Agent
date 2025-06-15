import os


# Set these early so they take effect before anything uses them
os.environ["GOOGLE_VERTEXAI_PROJECT"] = "apt-advantage-461615-m4"
os.environ["GOOGLE_VERTEXAI_LOCATION"] = "us-central1"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\revathi\AppData\Roaming\gcloud\application_default_credentials.json"

import certifi
import pymongo
import vertexai
from google.adk.agents import Agent#, Tool, ToolReturn
from vertexai.language_models import TextEmbeddingModel 
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import re
from word2number import w2n
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from google.cloud import storage
from dateutil.parser import parse as parse_date


# Load environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\revathi\AppData\Roaming\gcloud\application_default_credentials.json"
PROJECT_ID = "apt-advantage-461615-m4" 
PROJECT_LOCATION = "us-central1" 
DATABASE_NAME = "Manufacturing_Sensor"
COLLECTION_NAME = "manufacturing-sensor-hourly-snapshot"
username = quote_plus("*******")
password = quote_plus("*******")
CONNECTION_STRING  = f"mongodb+srv://{username}:{password}@cluster0.ihjjs0q.mongodb.net/"

# Init Vertex AI
#vertexai.init(project=PROJECT_ID, location=PROJECT_LOCATION)

# Load embedding model
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# ========== EMBEDDING UTILITY ==========
def generate_embedding(query: str):
    return embedding_model.get_embeddings([query])[0].values

# ========== MONGODB UTILITY ==========
def get_mongo_collection():
    client = pymongo.MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
    return client[DATABASE_NAME][COLLECTION_NAME]

# ========== TOOL FUNCTIONS ==========

def extract_hours_from_text(text: str) -> int:
    text = text.lower()

    # Try to extract digits first (e.g., "last 3 hours")
    match = re.search(r"(\d+)\s*(hour|hr|hrs|hours)", text)
    print("match------------------->",match)
    if match:
        return int(match.group(1))

    # Try converting word numbers to digits (e.g., "last two hours")
    try:
        words = re.search(r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(hour|hr|hrs|hours)", text)
        if words:
            return w2n.word_to_num(words.group(1))
    except Exception:
        pass

    return 1  # Default to 1 hour if nothing matched


def machines_turned_faulty_past_hour(natural_language_input: str) -> list:
    collection = get_mongo_collection()
    
    hours = extract_hours_from_text(natural_language_input)
    
    now = int(datetime.now().timestamp())
    past_time = now - hours * 3600

    return list(collection.find({
        "Faulty": True,
        "date_hour": {"$gte": past_time}
    }, {
        "_id": 0,
        "Machine_ID": 1,
        "fault_probability": 1,
        "avg_temperature": 1,
        "date_hour": 1
    }))


def find_similar_machine_events(query: str) -> list:
    collection = get_mongo_collection()
    query_embedding = generate_embedding(query)
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "default",  
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": 5
            }
        },
        {
            "$project": {
                "_id": 0,
                "Machine_ID": 1,
                "fault_probability": 1,
                "Faulty": 1,
                "avg_temperature": 1,
                "avg_vibration": 1,
                "date_hour": 1,
                "record_count": 1
            }
        }
    ]
    
    return list(collection.aggregate(pipeline))

def machines_turned_faulty_last_2_hours(_: str) -> list:
    collection = get_mongo_collection()
    now = int(datetime.now().timestamp())
    two_hours_ago = now - 2 * 3600

    return list(collection.find({
        "Faulty": True,
        "date_hour": {"$gte": two_hours_ago}
    }, {
        "_id": 0,
        "Machine_ID": 1,
        "fault_probability": 1,
        "avg_temperature": 1,
        "date_hour": 1
    }))
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import re
from datetime import datetime

import re
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from typing import Union, Dict

def upload_image_to_gcs(image_bytes, filename, bucket_name):
    #client = storage.Client()
    client = storage.Client.from_service_account_json(r"C:\Users\revathi\Downloads\cred.json")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/png")
    #blob.make_public()

    url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(hours=1),
    method="GET"
    )
 
    #return blob.public_url
    print("url------------------------->",url)
    return url
 
def plot_machine_trend(natural_query: str) -> str:
    """
    Parses a natural language query and returns a base64-encoded chart image (as Markdown)
    showing the trend of temperature or vibration for a given machine ID.
    """
    collection = get_mongo_collection()

    # Identify the metric
    metric = "temperature" if "temp" in natural_query.lower() else "vibration"
    metric_field = "avg_temperature" if metric == "temperature" else "avg_vibration"

    # Extract numeric machine ID
    match = re.search(r"machine[_\s]?(\d+)", natural_query.lower())
    if not match:
        return "⚠️ Could not extract a numeric machine ID. Try phrases like 'machine 5' or 'machine_10'."

    try:
        machine_id = int(match.group(1))  # Convert to integer for MongoDB query
    except Exception:
        return "⚠️ Could not parse machine ID as an integer."

    # Query MongoDB for that machine ID
    cursor = collection.find(
        {"Machine_ID": machine_id},
        {"_id": 0, "hour": 1, metric_field: 1}
    ).sort("hour", 1)

    data = list(cursor)
    if not data:
        return f"⚠️ No data found for machine `{machine_id}`."

    timestamps = []
    values = []
    for d in data:
        hour_value = d.get("hour")
        if isinstance(hour_value, (int, float)):
            dt = datetime.fromtimestamp(hour_value)
        elif isinstance(hour_value, str):
            try:
                dt = datetime.fromisoformat(hour_value)
            except ValueError:
                continue
        elif isinstance(hour_value, datetime):
            dt = hour_value
        else:
            continue

        timestamps.append(dt)
        values.append(d.get(metric_field, 0))

    if not timestamps or not values:
        return "⚠️ Unable to generate chart due to missing or invalid data."

    # Plot chart
    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, values, marker='o', color='blue')
    plt.title(f"{metric.title()} Trend for Machine {machine_id}")
    plt.xlabel("Time")
    plt.ylabel(metric.title())
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Convert to base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    #img_bytes = base64.b64encode(buffer.read()).decode("utf-8")
    img_bytes = buffer.getvalue()

    plt.close()

        # Upload to GCS (set your bucket name)
    public_url = upload_image_to_gcs(img_bytes, f"machine_{machine_id}_{metric}_trend.png", "machine-sensor-data")

    #return f"### 📊 {metric.title()} Trend for Machine `{machine_id}`\n\n" \
    #       f"![Chart](data:image/png;base64,{img_b64})"

    #return {
    #    "filename": f"machine_{machine_id}_{metric}_trend.png",
    #    "content": buffer.read(),
    #    "mimetype": "image/png"
    #}

    return f"### 📊 {metric.title()} Trend for Machine `{machine_id}`\n\n![Chart]({public_url})"
    #return f"📊 {metric.title()} Trend for Machine {machine_id}: {public_url}"


def parse_specific_date(text: str) -> int:
    """
    Parses a specific date from the input text and returns the start-of-day UNIX timestamp.
    Accepts formats like 'June 13', '2024-12-01', '13 June'.
    """
    date_patterns = re.findall(r'\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[a-z]{0,2}\s+[A-Za-z]+|[A-Za-z]+\s+\d{1,2})\b', text)
    for dp in date_patterns:
        try:
            dt = parse_date(dp)
            return int(datetime(dt.year, dt.month, dt.day).timestamp())
        except Exception:
            continue
    return None  # No valid date found

def machines_with_high_metrics(natural_language_input: str) -> list:
    """
    Filters machines with avg_temperature or avg_vibration thresholds, optionally filtered by date.
    Returns only distinct Machine_IDs.
    """
    collection = get_mongo_collection()

    # Parse metric thresholds
    pattern = re.compile(r"(temperature|vibration|temp)[^\d><=]*(>=|<=|>|<|=)?\s*(\d+)", re.IGNORECASE)
    matches = pattern.findall(natural_language_input)

    if not matches:
        return ["⚠️ Could not determine any valid temperature or vibration thresholds from your query."]

    query = {}
    for metric, operator, value in matches:
        field = "avg_temperature" if "temp" in metric.lower() else "avg_vibration"
        operator = operator or ">"
        value = float(value)

        mongo_op = {
            ">": "$gt",
            ">=": "$gte",
            "<": "$lt",
            "<=": "$lte",
            "=": "$eq"
        }.get(operator)

        if mongo_op:
            query[field] = {mongo_op: value}

    # Add date filter if present
    timestamp = parse_specific_date(natural_language_input)
    if timestamp:
        end_of_day = timestamp + 86400
        query["date_hour"] = {"$gte": timestamp, "$lt": end_of_day}

    # Fetch only Machine_IDs
    results = collection.find(query, {"_id": 0, "Machine_ID": 1})

    # Return unique Machine_IDs
    machine_ids = sorted({doc["Machine_ID"] for doc in results if "Machine_ID" in doc})

    return machine_ids if machine_ids else ["✅ No machines matched the condition(s)."]

from datetime import datetime, timedelta

def last_faulty_time(machine_id: int) -> str:
    collection = get_mongo_collection()

    # Query to match all variations of "Faulty" field (1, True, "true")
    query = {
        "Machine_ID": machine_id,
        "Faulty": {"$in": [True, 1, "true"]}
    }

    result = collection.find(query).sort("hour", -1).limit(1)

    record = next(result, None)

    if not record:
        return f"✅ Machine {machine_id} has not turned faulty so far."

    dt = record.get("hour")
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    elif isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt)

    return f"⚠️ Machine {machine_id} last turned faulty on {dt.strftime('%Y-%m-%d %H:%M:%S')}."

def faulty_machines_summary(natural_language_input: str) -> dict:
    collection = get_mongo_collection()
    
    hours = extract_hours_from_text(natural_language_input)
    
    now = int(datetime.now().timestamp())
    past_time = now - hours * 3600

    # Find distinct Machine_IDs where Faulty = True / 1 / "true"
    machine_ids = collection.distinct("Machine_ID", {
        "Faulty": {"$in": [True, 1, "true"]},
        "date_hour": {"$gte": past_time}
    })

    count = len(machine_ids)

    if count == 0:
        return {
            "message": "✅ No machines turned faulty in the specified time.",
            "count": 0,
            "machine_ids": []
        }

    return {
        "message": f"⚠️ {count} machine(s) turned faulty in the past {hours} hour(s).",
        "count": count,
        "machine_ids": machine_ids
    }

# ========== AGENT ==========

root_agent = Agent(
    name="sensor_monitoring_agent", 
    model="gemini-2.0-flash",  # or "gemini-2.0-pro"
    instruction="""
Start the conversation by introducing yourself as an Equipment Monitoring Assistant and ask how you can help in detecting sensor anomalies, find faulty machines, and analyze trends
""",
    tools=[
        find_similar_machine_events,
        #machines_turned_faulty_past_hour,
        plot_machine_trend,
        machines_with_high_metrics,
        last_faulty_time,
        faulty_machines_summary
    ]

)


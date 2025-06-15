from pymongo import MongoClient
import pandas as pd
from urllib.parse import quote_plus
import vertexai
from vertexai.language_models import TextEmbeddingModel
import os
import tiktoken
 
# Set your Google Cloud project and location
PROJECT_ID = "apt-advantage-461615-m4"
PROJECT_LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=PROJECT_LOCATION)
 
# MongoDB connection
username = quote_plus("********")
password = quote_plus("********")
mongo_uri = f"mongodb+srv://{username}:{password}@cluster0.ihjjs0q.mongodb.net/?connectTimeoutMS=60000"
client = MongoClient(mongo_uri)
db = client["Manufacturing_Sensor"]
collection = db["manufacturing-sensor-hourly-snapshot"]
 
# Load data
docs = list(collection.find({}))
df = pd.DataFrame(docs)
df["date_hour"] = df["hour"].astype("int64") // 10**9
 
# Define columns for embedding
features = [
    "avg_Error_Rate",
    "avg_Power_Consumption_kW",
    "avg_Production_Speed_units_per_hr",
    "avg_temperature",
    "avg_vibration",
    "fault_probability",
    "Faulty",
    "date_hour",
    "Machine_ID",
    "record_count"
]
 
# Drop rows with missing values
df = df.dropna(subset=features)
 
# Create descriptive text for each row
def row_to_text(row):
    return (
        f"Machine {row['Machine_ID']} | "
        f"Error Rate: {row['avg_Error_Rate']}, "
        f"Power: {row['avg_Power_Consumption_kW']} kW, "
        f"Speed: {row['avg_Production_Speed_units_per_hr']} units/hr, "
        f"Temp: {row['avg_temperature']} C, "
        f"Vibration: {row['avg_vibration']}, "
        f"Fault Probability: {row['fault_probability']}, "
        f"Faulty: {row['Faulty']}, "
        f"DateHour: {row['date_hour']}, "
        f"Record Count: {row['record_count']}"
    )
 
# Add embedding text and token count columns
encoding = tiktoken.get_encoding("cl100k_base")
MAX_TOKENS = 16000
MAX_INSTANCES = 250
 
df["embedding_text"] = df.apply(row_to_text, axis=1)
df["token_count"] = df["embedding_text"].apply(lambda text: len(encoding.encode(text)))
 
# Batching function with strict token limit
def build_batches_strict(df, max_tokens=MAX_TOKENS, max_instances=MAX_INSTANCES):
    batches = []
    current_batch = []
    current_token_count = 0
 
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        text = row_dict["embedding_text"]
        token_count = row_dict["token_count"]
 
        # Truncate if a single row exceeds token limit
        if token_count > max_tokens:
            print(f"Truncating row with {token_count} tokens to {max_tokens}")
            text = encoding.decode(encoding.encode(text)[:max_tokens])
            token_count = len(encoding.encode(text))
            row_dict["embedding_text"] = text
            row_dict["token_count"] = token_count
 
        # If adding this row would exceed limits, start a new batch
        if (len(current_batch) >= max_instances) or (current_token_count + token_count > max_tokens):
            if current_batch:
                print(f"Batch {len(batches)+1}: {len(current_batch)} records, {current_token_count} tokens")
                batches.append(current_batch)
            current_batch = [row_dict]
            current_token_count = token_count
        else:
            current_batch.append(row_dict)
            current_token_count += token_count
 
    if current_batch:
        print(f"Batch {len(batches)+1}: {len(current_batch)} records, {current_token_count} tokens")
        batches.append(current_batch)
 
    return batches
 
# Further split any batch that still exceeds the token limit
def split_batch_by_tokens(batch, max_tokens):
    sub_batches = []
    current_sub_batch = []
    current_token_count = 0
    for row in batch:
        token_count = row["token_count"]
        if token_count > max_tokens:
            # Truncate single row if needed
            text = row["embedding_text"]
            print(f"Truncating row with {token_count} tokens to {max_tokens}")
            text = encoding.decode(encoding.encode(text)[:max_tokens])
            token_count = len(encoding.encode(text))
            row["embedding_text"] = text
            row["token_count"] = token_count
        if current_token_count + token_count > max_tokens and current_sub_batch:
            sub_batches.append(current_sub_batch)
            current_sub_batch = [row]
            current_token_count = token_count
        else:
            current_sub_batch.append(row)
            current_token_count += token_count
    if current_sub_batch:
        sub_batches.append(current_sub_batch)
    return sub_batches
 
# Create initial batches
batches = build_batches_strict(df)
 
# Further split batches if needed
final_batches = []
for batch in batches:
    sub_batches = split_batch_by_tokens(batch, MAX_TOKENS)
    final_batches.extend(sub_batches)
 
# Load model
model = TextEmbeddingModel.from_pretrained("text-embedding-004")
 
# Process batches and update MongoDB
for batch_num, batch in enumerate(final_batches):
    total_tokens = sum(row["token_count"] for row in batch)
    print(f"Processing batch {batch_num + 1} with {len(batch)} records, {total_tokens} tokens")
    texts = [row["embedding_text"] for row in batch]
    try:
        embeddings = model.get_embeddings(texts)
        for i, row in enumerate(batch):
            embedding = embeddings[i].values
            collection.update_one({"_id": row["_id"]}, {"$set": {"embedding": embedding}})
    except Exception as e:
        print(f"Error in batch {batch_num + 1}: {e}")
 
print("Vertex AI embeddings stored in MongoDB for each record.")

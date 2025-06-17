# MachInsight-AI---Machine-Sensing-and-Monitoring-AI-Agent

**Application URL :**
https://machinsight-ai-297752632164.us-central1.run.app
**Sample Prompts : **
1. plot the temperature trend of machine 1
2. are there any machines with temperature greater than 45 in last one hour
3. When was the last time the machine 1 turned faulty
4. How many machines have turned faulty in last 2 hours?


# ⚙️ MachInsight AI – Real-Time Machine Sensing & Monitoring AI Agent

MachInsight AI is an intelligent real-time platform that empowers manufacturers to monitor sensor data, predict faults, and interact with their data using natural language — all powered by AI, machine learning, and vector search.

---

## 🚀 Inspiration

In today's fast-paced manufacturing environment, machine downtime can lead to massive productivity loss. We were inspired to build **MachInsight AI** to empower industries with a real-time, intelligent monitoring system that not only detects potential faults in advance but also enables users to interact with their sensor data through natural language. 

Our goal: bring together the best of **data warehousing, machine learning, vector databases, and AI agents** into a unified solution.

---

## 🤖 What It Does

MachInsight AI is a real-time IoT monitoring and diagnostics platform powered by AI. It:

- Ingests real-time sensor data into **BigQuery**
- Aggregates data hourly and predicts fault probability via **Random Forest ML**
- Stores results and semantic embeddings in **MongoDB**
- Builds a vector index with **MongoDB’s vector search**
- Powers an **AI Agent** using **Google ADK + Gemini 2.0 Flash** that can answer:
  - “Are there any machines with temperature greater than 45 today?”
  - “What’s the last time Machine 2 turned faulty?”
  - “Find machines similar to Machine 5’s fault behavior.”

---

## 🧱 How We Built It

- **Data Ingestion**: Real-time IoT sensor data sent to **BigQuery**
- **ML Pipeline**: Vertex AI Colab notebooks compute hourly summaries and apply a trained **Random Forest** model
- **Storage & Embeddings**: Output stored in **MongoDB**; embeddings created and indexed for vector search
- **Agent & Tools**: Agent built with Google ADK, including tools like:
  - `machines_with_high_metrics`
  - `last_faulty_time`
  - `faulty_machines_summary`
  - `plot_machine_trend`
  - `find_similar_machine_events`
- **Scheduling**: GCS and cron jobs orchestrate the notebook execution

---

## 🧗 Challenges We Ran Into

- ⏱ **Notebook Scheduling**: Ensuring ML and embeddings pipelines run in the right sequence
- 🧠 **Natural Language Parsing**: Mapping vague user questions to precise MongoDB queries
- 🎯 **Vector Search Tuning**: Crafting meaningful embeddings and similarity thresholds
- 🔐 **Access Issues**: Solving signed URL and GCS permission problems during dynamic chart generation

---

## 🏆 Accomplishments We're Proud Of

- A seamless end-to-end pipeline from **sensor ingestion to AI interaction**
- Modular agent with plug-and-play tools for analytics and visualization
- Harmonized stack: **BigQuery**, **Vertex AI**, **MongoDB**, **ADK**, **Gemini**
- Real-time, intelligent interaction on IoT data with predictive maintenance insights

---

## 📚 What We Learned

- ML pipeline orchestration using **Vertex AI Colab Enterprise**
- Semantic search with **MongoDB vector search**
- How to build AI agents with **Google ADK + Gemini**, including multi-turn contextual chat
- Best practices for **data modeling** and **real-time analytics** in IoT

---

## 🔮 What’s Next for MachInsight AI

- Integrate **anomaly detection** using autoencoders or LSTM models
- Expand support for **image/video sensors** for visual fault detection
- Enable **automated triggers** for repairs and alerting
- Build a **Looker Studio dashboard** + embed **agent chat widget**
- Explore **Edge AI deployment** to run insights at the factory floor

---

## 🧰 Tech Stack

- **BigQuery** – Real-time data warehouse
- **Vertex AI** – ML model training and prediction pipelines
- **MongoDB + Atlas Vector Search** – Data & embeddings storage with semantic search
- **Google ADK + Gemini** – AI Agent platform with LLM integration
- **Cloud Run / Docker** – Deployment infrastructure

---

## 📎 License

[MIT](LICENSE)

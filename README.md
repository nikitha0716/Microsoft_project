# 🚨 OpsMind

## Memory-Powered AI Incident Response Agent

OpsMind is an AI-powered Incident Response Agent that uses persistent memory to remember previous production incidents, their root causes, resolutions, successful runbooks, resolution times, and post-mortems.

When a new production incident occurs, OpsMind retrieves similar historical incidents from Hindsight memory and uses an LLM to recommend an evidence-based resolution.

---

# 🎯 Problem

Production incidents are often repetitive.

Engineers may encounter the same class of failure multiple times, but the knowledge about previous incidents is frequently distributed across:

- Incident tickets
- Runbooks
- Slack conversations
- Documentation
- Post-mortems
- Personal knowledge

During an outage, engineers spend valuable time rediscovering how similar incidents were solved.

OpsMind addresses this problem by creating persistent operational memory.

---

# 💡 Solution

OpsMind remembers previous incidents and learns from their outcomes.

The workflow is:

New Incident
↓
Hindsight Memory Recall
↓
Similar Historical Incidents
↓
Root Cause Analysis
↓
Successful Resolution Identification
↓
Runbook Recommendation
↓
Engineer Resolution
↓
Post-Mortem
↓
Hindsight Memory Update
↓
Improved Future Responses

---

# 🧠 Why Memory Matters

A normal LLM can analyze an incident based on the information provided in the current prompt.

OpsMind goes further.

It retrieves historical operational knowledge before generating its recommendation.

For example:

A new Payment API incident reports:

HTTP 503
Database timeout
Connection pool exhausted

OpsMind recalls previous incidents where:

- The same service experienced HTTP 503 errors.
- Database connection pools were exhausted.
- Increasing the connection pool resolved the issue.
- The runbook `payment-db-connection-pool-v2` was successful.

The agent uses this historical evidence to recommend a resolution.

---

# 🏗️ Architecture

User
│
▼
Streamlit UI
│
├───────────────┐
│               │
▼               ▼
Investigate    Teach OpsMind
Incident
│               │
▼               ▼
Hindsight Memory
│
├── Retain
│
└── Recall
│
▼
Historical Incidents
│
▼
Groq LLM
│
▼
Incident Diagnosis
│
▼
Resolution Recommendation

---

# 🔧 Technology Stack

## Frontend

Streamlit

## AI / LLM

Groq

## Memory

Hindsight by Vectorize

## Programming Language

Python

## Configuration

python-dotenv

---

# 🧠 Hindsight Usage

OpsMind uses Hindsight as its persistent memory layer.

## Retain

Resolved incidents are stored using Hindsight's retain operation.

Stored information includes:

- Incident ID
- Service
- Severity
- Symptoms
- Root cause
- Resolution
- Runbook
- Outcome
- Resolution time
- Post-mortem

## Recall

When a new incident occurs, OpsMind queries Hindsight for similar historical incidents.

The retrieved memories are passed to the AI analysis layer.

---

# 🚨 Example Incident

## Current Incident

Service:

Payment API

Severity:

SEV-1

Logs:

HTTP 503 Service Unavailable

Connection pool exhausted.

Database connection timeout.

Retry attempts exceeded.

---

# 🧠 Historical Memory

OpsMind retrieves previous incidents such as:

INC-1821

Root Cause:
Database connection pool exhaustion.

Resolution:
Increased connection pool from 50 to 100.

Runbook:
payment-db-connection-pool-v2

Outcome:
SUCCESS

Resolution Time:
7 minutes

---

# 🤖 AI Recommendation

Likely Root Cause:

Database connection pool exhaustion.

Recommended Runbook:

payment-db-connection-pool-v2

Recommended Action:

Increase the database connection pool and restart the payment service.

Historical Evidence:

Similar incidents were successfully resolved using the same remediation pattern.

---

# 📋 Post-Mortem Learning

After an incident is resolved, engineers can teach OpsMind about the incident.

The post-mortem becomes part of the persistent memory.

This allows future incidents to benefit from previous operational experience.

---

# 📁 Project Structure

OpsMind/

├── app.py

├── hindsight_service.py

├── ai_service.py

├── incident_data.py

├── requirements.txt

├── .env

├── .env.example

├── .gitignore

├── README.md

│

└── data/

    └── sample_incidents.json

---

# ⚙️ Installation

Clone the repository:

git clone YOUR_GITHUB_REPOSITORY_URL

Move into the project:

cd OpsMind

Create a virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

---

# 🔐 Environment Variables

Create a `.env` file.

Add:

HINDSIGHT_API_KEY=your_hindsight_api_key

HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io

HINDSIGHT_BANK_ID=opsmind-incidents

GROQ_API_KEY=your_groq_api_key

GROQ_MODEL=openai/gpt-oss-20b

---

# ▶️ Running the Application

Run:

streamlit run app.py

Open:

http://localhost:8501

---

# 🧪 Demo Workflow

## Step 1

Open OpsMind.

## Step 2

Go to:

Teach OpsMind

## Step 3

Store historical incidents.

Example:

INC-1821

Payment API

SEV-1

Root Cause:
Database connection pool exhaustion

Resolution:
Increase connection pool and restart payment service

Runbook:
payment-db-connection-pool-v2

Outcome:
SUCCESS

---

## Step 4

Repeat for several historical incidents.

---

## Step 5

Go to:

Investigate Incident

---

## Step 6

Enter:

Service:

Payment API

Severity:

SEV-1

Logs:

HTTP 503 Service Unavailable.

Connection pool exhausted.

Database connection timeout.

Retry attempts exceeded.

---

## Step 7

Click:

Investigate Incident

---

## Step 8

OpsMind retrieves historical memories.

---

## Step 9

The LLM analyzes the current incident together with historical evidence.

---

## Step 10

OpsMind recommends a proven resolution and runbook.

---

# 🎥 Hackathon Demo Story

Imagine a production Payment API is down.

An engineer receives an HTTP 503 alert.

Instead of manually searching through old incidents, the engineer asks OpsMind.

OpsMind remembers that the same failure occurred previously.

It finds the root cause.

It identifies the successful runbook.

It shows how long the previous incidents took to resolve.

It recommends the previously successful remediation.

After the new incident is resolved, the post-mortem is stored back into memory.

The next incident can benefit from this new knowledge.

---

# 🔄 Learning Loop

Incident

↓

Recall Historical Memory

↓

AI Recommendation

↓

Engineer Resolution

↓

Post-Mortem

↓

Hindsight Retain

↓

Updated Operational Memory

↓

Better Future Investigation

---

# 🔒 Security

API keys are stored in `.env`.

`.env` is excluded from Git using `.gitignore`.

Never commit:

- Hindsight API keys
- Groq API keys
- Credentials
- Production secrets

---

# 🚀 Future Improvements

Possible future versions could include:

- Slack integration
- PagerDuty integration
- Jira integration
- Kubernetes log ingestion
- Automatic incident classification
- Incident severity prediction
- Runbook execution
- Post-mortem generation
- Observability integrations
- Grafana integration
- Prometheus integration
- Team-specific memory banks
- Incident dashboards
- Timeline visualization
- Automated remediation with human approval

---

# 🏆 Hackathon Value

OpsMind demonstrates:

- Persistent AI memory
- Retrieval of historical operational knowledge
- AI-assisted incident investigation
- Learning from post-mortems
- Evidence-based recommendations
- Real-world DevOps use case
- Human-in-the-loop incident response

---

# 👥 Team

Project:

OpsMind

Category:

Engineering & DevOps

Use Case:

AI Incident Response Agent

Core Technology:

Hindsight Memory

AI:

Groq

Interface:

Streamlit

---

# 📜 License

MIT License
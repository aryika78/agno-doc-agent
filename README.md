# 📘 Agentic Document Processing System

An **agentic document AI assistant** built using **Agno**, **Streamlit**, **Qdrant**, and **Azure OpenAI**. A single Agno Agent (gpt-5-nano) handles QA, summarization, and entity extraction over **PDF / DOCX / TXT** files — the LLM decides how to respond based on the user's query.

---

## ✨ Features

* Upload and persist **PDF / DOCX / TXT** documents
* Chat with a selected document (grounded in document content)
* **QA, summarization, entity extraction, JSON output** — all handled by one Agno Agent
* **Multi-intent queries** (e.g. "summarize and extract entities") — handled naturally in one response
* **LLM-driven** — no rule-based routing, the model decides how to respond
* Qdrant-backed **persistent vector storage** (no duplicate indexing)
* Safe document lifecycle: Upload, Replace (explicit confirmation), Delete
* Streamlit chat UI with document switching

---

## 🧠 Design Philosophy

> **One agent, one LLM call, one response.**

* A single Agno `Agent` with combined instructions handles all query types
* The LLM reads the query and decides whether to summarize, answer, extract entities, or do multiple tasks
* No Team, no routing, no delegation — the simplest architecture that works reliably
* Qdrant is the **single source of truth** for documents

---

## 🏗️ Project Structure

```
AGNO_DOC_AGENT/
├── agents/
│   └── agno_agents.py              # Agno Agent definition
│
├── config/
│   └── qdrant_client.py            # Qdrant connection
│
├── prompts/
│   └── agent_prompt.py             # Agent instructions
│
├── storage/
│   ├── chunking.py                 # Document chunking
│   └── document_store.py           # Qdrant-backed persistence
│
├── app.py                          # Streamlit application
├── document_loader.py              # PDF/DOCX/TXT loader
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🏛️ Architecture

```
User Query
    ↓
DocumentStore.search() → retrieves relevant chunks from Qdrant
    ↓
Agno Agent (gpt-5-nano) → reads document context + query, responds directly
    ↓
Response returned to user
```

One LLM call per query. The agent's instructions cover QA, summarization, entity extraction, and JSON output. The LLM decides what to do based on the query.

---

## 🚀 Setup Instructions

### 1) Clone the repository

```bash
git clone https://github.com/aryika78/agno-doc-agent.git
cd agno-doc-agent
```

### 2) Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Unix
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 5) Create `.env`

```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
DEPLOYMENT_REASONING=your_5_nano_deployment
```

---

## ▶️ Running the System

```bash
streamlit run app.py
```

---

## 🧪 Example Queries

* what is this document about?
* summarize this document in 3 bullet points
* who signed the agreement?
* extract all people and organizations
* summarize and extract all entities
* list all projects as json
* what are the payment terms?

---

## 🧰 Tech Stack

**Core**
* Python
* Streamlit

**AI / LLM**
* Agno (Agent framework)
* Azure OpenAI (gpt-5-nano)

**Document Processing**
* PyPDF2
* python-docx

**Vector Search & Storage**
* Qdrant
* FastEmbed (BAAI/bge-small-en-v1.5)

---

## 👩‍💻 Author

**Aryika Patni**

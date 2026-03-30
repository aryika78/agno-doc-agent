# Agentic Document Processing System

An **agentic document AI assistant** built using **Agno**, **Streamlit**, **Qdrant**, and **Azure OpenAI**. A single Agno Agent (gpt-5-nano) handles QA, summarization, entity extraction, visualizations, and more over **PDF / DOCX / TXT** files (including scanned PDFs via OCR) — the LLM decides how to respond based on the user's query.

---

## Features

* Upload and persist **PDF / DOCX / TXT** documents (including **scanned/image PDFs** via OCR)
* Chat with a selected document (grounded in document content)
* **QA, summarization, entity extraction, visualizations, JSON output** — all handled by one Agno Agent
* **Smart visualizations** — bar, pie, grouped bar, stacked bar, timeline/Gantt, and table charts via Plotly
* **Conversation memory** — agent remembers the last 4 exchanges for context (resolves pronouns, references)
* **Suggested questions** — auto-generated on upload/document switch, diverse and content-focused
* **Follow-up suggestions** — auto-generated after each response, with topic-exhaustion detection
* **Document insights sidebar** — one-click deep analysis with adaptive sections based on document type
* **Multi-intent queries** (e.g. "summarize and extract entities") — handled naturally in one response
* **RAG guardrails** — agent refuses to chart or answer when data isn't in the document
* Qdrant-backed **persistent vector storage** (no duplicate indexing)
* Safe document lifecycle: Upload, Replace (explicit confirmation), Delete

---

## Design Philosophy

> **One agent, one LLM call, one response.**

* A single Agno `Agent` with combined instructions handles all query types
* The LLM reads the query and decides whether to summarize, answer, extract entities, visualize, or do multiple tasks
* No Team, no routing, no delegation — the simplest architecture that works reliably
* Qdrant is the **single source of truth** for documents

---

## Project Structure

```
AGNO_DOC_AGENT/
├── agents/
│   └── agno_agents.py              # Agno Agent definition
│
├── config/
│   └── qdrant_client.py            # Qdrant connection
│
├── prompts/
│   └── agent_prompt.py             # Agent instructions (QA, summary, charts, etc.)
│
├── storage/
│   ├── chunking.py                 # Document chunking
│   └── document_store.py           # Qdrant-backed persistence + full text retrieval
│
├── app.py                          # Streamlit application (chat, charts, insights, suggestions)
├── document_loader.py              # PDF/DOCX/TXT loader with OCR fallback
├── requirements.txt
├── .env.example                    # Environment variable template
├── README.md
└── .gitignore
```

---

## Architecture

```
User Query
    ↓
build_chat_input() → adds conversation history to the query
    ↓
Tool Agent (gpt-5-nano) → decides what context it needs
    ↓
Calls search_document() or get_full_text() → retrieves from Qdrant
    ↓
Agent generates response (text, JSON, or chart JSON)
    ↓
render_message() → renders as markdown, JSON block, or Plotly chart
```

The agent is **agentic** — it decides what to retrieve from the document using its tools, rather than receiving pre-fetched context. It can search multiple times if needed. The agent's instructions cover QA, summarization, entity extraction, visualizations, and JSON output.

---

## Setup Instructions

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

### 4) Install Tesseract OCR (for scanned PDF support)

- Download from [UB-Mannheim/tesseract releases](https://github.com/UB-Mannheim/tesseract/releases)
- Install to default path: `C:\Program Files\Tesseract-OCR`
- Set the `TESSERACT_CMD` in your `.env` file if not on PATH (see `.env.example`)

### 5) Install Poppler (for scanned PDF support)

- Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases)
- Extract and note the path to the `Library\bin` folder
- Set the `POPPLER_PATH` in your `.env` file (see `.env.example`)

### 6) Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 7) Create `.env`

Copy `.env.example` to `.env` and fill in your values:

```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
DEPLOYMENT_REASONING=your_5_nano_deployment
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\path\to\poppler\Library\bin
```

---

## Running the System

```bash
streamlit run app.py
```

---

## Example Queries

* what is this document about?
* summarize this document in 3 bullet points
* who signed the agreement?
* extract all people and organizations
* summarize and extract all entities
* list all projects as json
* compare the technologies used across projects as a bar chart
* show the project timeline as a Gantt chart
* what are the payment terms?

---

## Tech Stack

**Core**
* Python
* Streamlit

**AI / LLM**
* Agno (Agent framework)
* Azure OpenAI (gpt-5-nano)

**Document Processing**
* PyPDF2 (text PDFs)
* Tesseract + pdf2image (scanned/image PDFs via OCR)
* python-docx

**Visualization**
* Plotly (bar, pie, grouped bar, stacked bar, timeline/Gantt, table)

**Vector Search & Storage**
* Qdrant
* FastEmbed (BAAI/bge-small-en-v1.5)

---

## Author

**Aryika Patni**

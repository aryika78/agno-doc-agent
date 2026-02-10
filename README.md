# 📘 Prompt-Orchestrated Multi-Agent Document Processing System

A **production-grade Prompt-Orchestrated Multi-Agent Document AI Assistant** built using **Streamlit**, **Qdrant**, **Agno-style agent orchestration**, and Azure OpenAI models. The system provides deterministic, multi-intent document understanding over **PDF / DOCX / TXT** files with strict separation of text and JSON outputs.

---

## ✨ Features 

* Upload and persist **PDF / DOCX / TXT** documents
* Chat with a selected document (grounded strictly in document content)
* **Multi-intent queries in a single sentence** (QA + summary + entities + JSON)
* Deterministic **bullet summaries** (length-aware, text-only)
* **Structured JSON extraction** (only when explicitly requested)
* **Factual entity extraction only**:

  * Dates
  * People
  * Organizations
  * Locations
  * Amounts
* No hallucinated entities or inferred concepts
* Qdrant-backed **persistent vector storage** (no duplicate indexing)
* Safe document lifecycle:

  * Upload
  * Replace (explicit confirmation)
  * Delete
* Streamlit chat UI with **JSON prettify toggle**
* Document switching without restart
* Stable behavior across Streamlit reruns

---

## 🧠 Design Philosophy

> **The prompt defines the contract. Orchestration enforces the rules.**

* A central **OrchestratorAgent** controls intent resolution and agent execution
* **Rule-based intent classification** – the orchestrator uses `classify_intent()` with keyword/regex rules (not an LLM-based router)
* Each agent is backed by a strict, single-purpose prompt via **agno_tools**
* Deterministic intent priority prevents output mixing
* **JSON and text outputs are never merged**
* Qdrant is treated as the **single source of truth** for documents

---

## 🏗️ Project Structure 

```
AGNO_DOC_AGENT/
├── agents/
│   ├── agno_agents.py                 # Agno Agent definitions (QA, Summary, Entity)
│   ├── document_analyst_agent.py      # QA + Summary
│   ├── extraction_agent.py            # Entities + JSON
│   ├── orchestrator_agent.py          # Intent logic & priority
│   └── response_composer_agent.py     # Output normalization
│
├── config/
│   └── qdrant_client.py                # Qdrant connection
│
├── prompts/
│   ├── classifier_prompt.py
│   ├── entity_prompt.py
│   ├── json_prompt.py
│   ├── orchestrator_prompt.py
│   ├── qa_prompt.py
│   ├── router_prompt.py
│   └── summary_prompt.py
│
├── storage/
│   ├── chunking.py                     # Document chunking
│   └── document_store.py               # Qdrant-backed persistence
│
├── tools/
│   ├── agno_tools.py                  # QA, summary, entity (used by analyst & extractor)
│   ├── classifier_tool.py
│   ├── entity_tool.py
│   ├── json_tool.py
│   ├── qa_tool.py
│   └── summary_tool.py
│
├── app.py                              # Streamlit application
├── main.py
├── document_loader.py
├── azure_client.py
├── requirements.txt
├── README.md
└── .gitignore
```


---

## 📋 Implementation Notes

**Tool usage**
* **agno_tools** (`qa_from_document`, `summarize_document`, `extract_entities_from_document`) – used by `DocumentAnalystAgent` and `ExtractionAgent`
* **classifier_tool** – used by `DocumentAnalystAgent` for document classification
* Legacy tools (`entity_tool`, `json_tool`, `qa_tool`, `summary_tool`) exist but are **not used**; the analyst and extractor call `agno_tools` directly

**Agno integration**
* `agno_agents.py` defines `QA_AGENT`, `SUMMARY_AGENT`, `ENTITY_AGENT` with Agno `Agent` and tools
* Execution path: the analyst and extractor call the tool functions directly; `agent.run()` is **not** used

**Prompts**
* `ORCHESTRATOR_PROMPT` and `ROUTER_PROMPT` exist but are **not used**; the orchestrator uses rule-based `classify_intent()` instead

**Document context**
* **Streamlit (`app.py`)**: Uses vector search to fetch relevant chunks as context; that context is passed to the orchestrator
* **CLI (`main.py`)**: Passes the full document text to the orchestrator

---

## 🧠 Intent Orchestration (Core Logic)

Supported intents:

* `qa` – natural language answers
* `summary` – clean text summary
* `entities` – factual entity listing (text)
* `json` – structured JSON output

### Priority Rules 

```
summary → json → qa → entities
```

Hard guarantees:

* Any request mentioning **json** returns JSON only
* JSON is never mixed with text output
* Summary never includes entities or structured data
* If `json` exists → entities are skipped
* If `summary` exists → QA is skipped

Multi-intent queries are supported using connectors like:

* `then`
* `also`
* `next`

---

## 📦 JSON Handling

* JSON is produced **only when explicitly requested**
* Returned once, in raw form
* UI provides a **prettify toggle** (raw ↔ formatted)
* Toggle appears **only for valid JSON blocks**

---

## 🗂️ Document Persistence (Qdrant)

* Qdrant is the single source of truth
* Streamlit session state is hydrated from Qdrant on app start
* Duplicate indexing is prevented
* Safe document replacement with explicit confirmation
* Delete action removes vectors and resets UI state

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
venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

Additionally, install **Qdrant** and **FastEmbed** for vector storage and embeddings (required for Streamlit):

```bash
pip install qdrant-client fastembed
```

Ensure Qdrant is running locally (default: `localhost:6333`).

### 4) Create `.env`

Create a file named `.env` in the project root:

```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
DEPLOYMENT_CLASSIFIER=your_4_1_nano_deployment
DEPLOYMENT_SUMMARY=your_4_1_nano_deployment
DEPLOYMENT_REASONING=your_5_nano_deployment
```

---

## ▶️ Running the System

```bash
streamlit run app.py
```

---

## 🧪 Example Queries

* summarize this document in 3 lines
* what is the project deadline
* extract people and dates
* extract entities then give json
* explain this document briefly
* who are the people mentioned

---

## 📌 Final System Guarantees

✔ Persistent, duplicate-free documents
✔ Stable Streamlit reruns
✔ Deterministic multi-intent handling
✔ Clean separation of text vs JSON
✔ No hallucinated entities
✔ Production-grade orchestration behavior

---
## 🧰 Tech Stack

**Core**

* Python
* Streamlit

**AI / LLM**

* Agno (multi-agent orchestration)
* Azure OpenAI

  * gpt-4.1-nano
  * gpt-5-nano

**Document Processing**

* PyPDF2
* python-docx

**Vector Search & Storage**

* Qdrant
* FastEmbed

---

## 👩‍💻 Author

**Aryika Patni**

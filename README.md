# 📘 Prompt-Orchestrated Multi-Agent Document Processing System (Agno + Multi‑Model Nano)

A tool-driven **multi-agent** document analysis system built with **Agno**, **gpt-4.1-nano**, and **gpt-5-nano** that performs reliable, format-controlled processing of **PDF / DOCX / TXT** files using carefully engineered prompts and deterministic agent orchestration.

---

## ✨ Features

* Bullet summary of any document (length-aware)
* Structured JSON extraction from unstructured text
* **Dynamic entity finder** (people, dates, money, locations, books, emails, animals, etc.)
* Question answering grounded strictly in document content with cross‑line reasoning
* Document type classification
* **Multi‑agent orchestration** instead of a single router
* Intent logging for explainability
* Session mode: switch documents without restarting

---

## 🧠 Design Philosophy

> **The prompt does the thinking. The model follows instructions.**

* A central **OrchestratorAgent** decides which agent to call
* Each agent wraps a strict prompt template
* Temperature = 0 for predictable outputs
* Uses **gpt-4.1-nano** for structuring tasks
* Uses **gpt-5-nano** for reasoning tasks
* Deterministic intent rules reduce LLM misrouting

---

## 🏗️ Updated Project Structure

```
agno_doc_agent/
├── main.py
├── document_loader.py
├── azure_client.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── agents/
│   ├── document_analyst_agent.py
│   ├── extraction_agent.py
│   ├── orchestrator_agent.py
│   └── response_composer_agent.py
│
├── prompts/
│   ├── summary_prompt.py
│   ├── router_prompt.py
│   ├── json_prompt.py
│   ├── entity_prompt.py
│   ├── qa_prompt.py
│   ├── classifier_prompt.py
│   └── orchestrator_prompt.py
│
└── tools/
    ├── summary_tool.py
    ├── json_tool.py
    ├── entity_tool.py
    ├── qa_tool.py
    └── classifier_tool.py
```

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
python main.py
```

You will be prompted to enter a document path.

Type `new` to load another document, or `exit` to quit.

---

## 🧪 Example Queries

* summarize this document in 2 lines
* what is the project deadline
* extract books
* extract animals then summarize briefly
* explain this document and give json
* who are the people mentioned
* list all dates

---

## 🔍 How It Works (New Flow)

```
User Query
   ↓
OrchestratorAgent
   ↓
Intent Classification (rule-based + prompt help)
   ↓
Relevant Agents Called in Sequence
   ↓
ResponseComposerAgent merges outputs
```

---

## 🧰 Tech Stack

* Python
* Agno
* Azure OpenAI (gpt-4.1-nano, gpt-5-nano)
* PyPDF2, python-docx

---

## 📌 Important Notes

* No document data is stored; everything runs in memory per session
* Prompts are model-agnostic; model usage is configuration-based
* System prints **[Intent]** and **[Agents]** for explainability

---

## 👩‍💻 Author

Aryika Patni

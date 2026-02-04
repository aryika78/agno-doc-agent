# 📘 Prompt-Orchestrated Document Processing Agent (Agno + Multi‑Model Nano)

A tool-driven document analysis agent built with **Agno**, **gpt-4.1-nano**, and **gpt-5-nano** that performs reliable, format-controlled processing of **PDF / DOCX / TXT** files using carefully engineered prompts and an LLM‑based router.

---

## ✨ Features

* Bullet summary of any document (length-aware)
* Structured JSON extraction from unstructured text
* **Dynamic entity finder** (works for people, dates, money, locations, books, emails, animals, etc.)
* Question answering grounded strictly in document content with cross‑line reasoning
* Document type classification
* **LLM-based intelligent routing** instead of keyword rules
* Session mode: switch documents without restarting

---

## 🧠 Design Philosophy

> **The prompt does the thinking. The model follows instructions.**

* LLM router decides the correct tool
* Each tool wraps a strict prompt template
* Temperature = 0 for predictable outputs
* Uses **gpt-4.1-nano** for structuring tasks
* Uses **gpt-5-nano** for reasoning tasks

---

## 🏗️ Project Structure

```
agno_doc_agent/
├── README.md
├── agent.py
├── router_llm.py
├── main.py
├── document_loader.py
├── azure_client.py
├── requirements.txt
├── .gitignore
│
├── prompts/
│   ├── summary_prompt.py
│   ├── json_prompt.py
│   ├── entity_prompt.py
│   ├── qa_prompt.py
│   ├── classifier_prompt.py
│   └── router_prompt.py
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

## ▶️ Running the Agent

```bash
python main.py
```

You will be prompted to enter a document path.

### Example queries

* summarize this document in 2 lines
* extract json
* extract people
* extract books
* extract emails
* what is the payment amount
* classify this document

Type `new` to load another document, or `exit` to quit.

---

## 🧪 Supported File Types

* `.txt`
* `.docx`
* `.pdf`

---

## 🔍 How It Works

```
User Query
   ↓
LLM Router (gpt‑5‑nano)
   ↓
Selected Tool
   ↓
Prompt Template + Document
   ↓
Correct Model (4.1‑nano or 5‑nano)
   ↓
Structured Output
```

---

## 🧰 Tech Stack

* Python
* Agno
* Azure OpenAI (`gpt-4.1-nano`, `gpt-5-nano`)
* PyPDF2, python-docx

---

## 📌 Notes

* No document data is stored; everything runs in memory per session
* Prompts are model-agnostic; routing and model usage are configuration-based
* Entity extraction is now dynamic based on user query

---

## 👩‍💻 Author

Aryika Patni

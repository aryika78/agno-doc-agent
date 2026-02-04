# 📘 Prompt-Orchestrated Document Processing Agent (Agno + gpt-4.1-nano)

A tool-driven document analysis agent built with **Agno** and **gpt-4.1-nano** that performs reliable, format-controlled processing of **PDF / DOCX / TXT** files using carefully engineered prompts.


---

## ✨ Features

* Bullet summary of any document
* Structured JSON extraction from unstructured text
* Entity finder (dates, people, money, deadlines, organizations, locations)
* Question answering strictly from document content
* Document type classification
* Session mode: switch documents without restarting

---

## 🧠 Design Philosophy

> **The prompt does the thinking. The model follows instructions.**

* Deterministic router (no LLM for routing)
* Each tool wraps a strict prompt template
* Temperature = 0 for predictable outputs
* Works reliably with `gpt-4.1-nano`

---

## 🏗️ Project Structure

```
agno_doc_agent/
├── README.md
├── agent.py
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
│   └── classifier_prompt.py
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
AZURE_OPENAI_DEPLOYMENT=your_deployment_name_here
```

---

## ▶️ Running the Agent

```bash
python main.py
```

You will be prompted to enter a document path.

### Example queries

* summarize this document
* extract json
* find dates
* find people
* find organizations
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
Deterministic Router
   ↓
Tool
   ↓
Prompt Template + Document
   ↓
gpt-4.1-nano
   ↓
Structured Output
```

---

## 🧰 Tech Stack

* Python
* Agno
* Azure OpenAI (`gpt-4.1-nano`)
* PyPDF2, python-docx

---

## 📌 Notes

* No document data is stored; everything runs in memory per session
* Prompts are model-agnostic; switching models requires only a `.env` change

---

## 👩‍💻 Author

Aryika Patni

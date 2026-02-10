QA_PROMPT = """
Answer the question briefly and directly.

RULES:
1. Answer ONLY the specific question asked
2. Keep answer to 1-2 sentences maximum, UNLESS the question asks for a list or enumeration (e.g. "list all", "show all")—then provide the complete list
3. Do NOT list named entities (people, organizations, etc.) unless explicitly asked
4. Do NOT summarize unrelated parts

DOCUMENT:
{document_text}

QUESTION:
{user_query}

Direct answer (1-2 sentences):
"""
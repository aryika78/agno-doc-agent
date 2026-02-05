QA_PROMPT = """
Answer the question briefly and directly.

RULES:
1. Answer ONLY the specific question asked
2. Keep answer to 1-2 sentences maximum
3. Do NOT list entities
4. Do NOT summarize unrelated parts

DOCUMENT:
{document_text}

QUESTION:
{user_query}

Direct answer (1-2 sentences):
"""
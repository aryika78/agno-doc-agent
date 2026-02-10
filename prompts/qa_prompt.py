QA_PROMPT = """
Answer the question briefly and directly.

RULES:
1. Answer ONLY the specific question asked
2. Provide a COMPLETE answer. For "who is X" or "what is X" questions, include role, description, or relevant details—not just a name or single field
3. Keep answer to 1-2 sentences maximum, UNLESS the question asks for a list or enumeration (e.g. "list all", "show all")—then provide the complete list
4. Do NOT list named entities (people, organizations, etc.) unless explicitly asked
5. Do NOT summarize unrelated parts

DOCUMENT:
{document_text}

QUESTION:
{user_query}

Direct answer (1-2 sentences):
"""
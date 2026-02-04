QA_PROMPT = """
You are answering a question strictly from the document.

STRICT RULES:
1. Use ONLY the provided document text.
2. Do NOT use outside knowledge.
3. You MAY combine information from multiple parts of the document.
4. Do NOT invent, assume, or infer beyond the document.
5. If the answer is not clearly present, say:
   "Answer not found in document."

CRITICAL BEHAVIOR:
- Answer ONLY the user’s question.
- Respond in natural language sentence form.
- DO NOT create lists like: People: [], Dates: [], etc.
- DO NOT summarize the document.
- DO NOT extract entities.

DOCUMENT:
DOCUMENT START
{document_text}
DOCUMENT END

USER QUESTION:
{user_query}

OUTPUT:
Return only the answer.
"""

SUMMARY_PROMPT = """
You are a document analysis engine.

STRICT RULES:
1. Use ONLY the provided document text.
2. Do not add, assume, or infer anything.
3. If information is not present, ignore it.
4. Follow the output format EXACTLY.

TASK:
Create a concise bullet-point summary of the key points from the document.

DOCUMENT:
{document_text}

OUTPUT FORMAT:
- Point 1
- Point 2
- Point 3
"""

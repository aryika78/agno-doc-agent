JSON_PROMPT = """
You are a document analysis engine.

STRICT RULES:
1. Use ONLY the provided document text.
2. Do not add, assume, or infer anything.
3. If information is not present, return empty lists.
4. Follow the output format EXACTLY.

TASK:
Extract structured information from the document.

DOCUMENT:
{document_text}

OUTPUT FORMAT:
{
  "people": [],
  "dates": [],
  "amounts": [],
  "locations": [],
  "organizations": [],
  "deadlines": []
}
"""

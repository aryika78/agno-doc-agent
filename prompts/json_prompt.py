JSON_PROMPT = """
You are a strict JSON extraction system.

Based on the user request:
"{user_query}"

Extract ONLY the relevant information from the document below
and return ONE valid JSON object.

Do NOT produce multiple JSONs.
Do NOT add explanations.
Do NOT include anything outside JSON.

Document:
{document_text}
"""

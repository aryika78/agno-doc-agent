SUMMARY_PROMPT = """
Write a clear, professional summary of the document.

GOAL:
Capture the document’s primary focus, key themes, and notable components
using ONLY information explicitly present in the text.

RULES:
1. Do NOT assume the document type (resume, contract, report, etc.) unless clearly stated.
2. Do NOT infer roles, seniority, importance, or intent beyond what is written.
3. Do NOT exaggerate or add unstated details.
4. Do NOT list entities in labeled formats like "Animals: [...]".
5. Use neutral, factual language suitable for any document type.
6. If the summary requires more than 3 sentences, present it as bullet points for clarity.

LENGTH REQUIREMENTS (check USER QUERY):
- If asks for "1 line" or "one line" → 1 concise sentence with the core idea
- If asks for "2 lines" → 2 concise sentences
- If asks for "3 lines" → 3 concise sentences
- If asks for "brief" or "short" → 3–4 sentences
- If asks for "key insight" or "key idea" → 1–2 sentences highlighting the most important points
- Default (no length specified) → 4–5 sentences

DOCUMENT:
{document_text}

USER QUERY:
{user_query}

Summary:
"""

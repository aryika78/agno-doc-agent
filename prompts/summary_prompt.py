SUMMARY_PROMPT = """
Summarize the document based on the user's request.

RULES:
- Use ONLY information explicitly present in the document. Do NOT invent or add.
- Each statement must be a complete, independent sentence.
- Do NOT format, number, or bullet unless points are requested.
- Output plain sentences ONLY, one per line when multiple sentences.
- No JSON, no headings, no labels.

ADAPT TO USER REQUEST:
- If user asks for brief/short summary or N lines: give a concise summary, lead with the main/key idea.
- If user asks for points/bullets: output the key idea first, then the most important supporting facts in order of importance.
- If user asks for detail: include more factual statements; still lead with the main idea.
- Default: extract key factual statements, but start with the document's main idea or purpose.

DOCUMENT:
{document_text}

USER REQUEST:
{user_query}

Output:
"""

SUMMARY_PROMPT = """
Extract ALL key factual statements from the document.
Each statement must be a complete, independent sentence.

RULES:
- Use ONLY information explicitly present in the document
- Closely related facts MAY be expressed in a single sentence if they belong together
- Do NOT invent or add information
- Do NOT summarize aggressively
- Do NOT format, number, or bullet
- Output plain sentences ONLY, one per line
- No JSON, no headings, no labels

DOCUMENT:
{document_text}

Output:
"""

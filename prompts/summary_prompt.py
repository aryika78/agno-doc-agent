SUMMARY_PROMPT = """
Summarize the document's main content.

RULES:
1. Focus on the primary subject (contract, agreement, report, etc.)
2. Cover: parties involved, key amounts, deadlines, main purpose
3. Do NOT list entities in format like "Animals: [...]"
4. Respect length requirements if specified

LENGTH REQUIREMENTS (check USER QUERY):
- If asks for "1 line" or "one line" → 1 bullet point with key insight
- If asks for "2 lines" → 2 bullet points
- If asks for "3 lines" → 3 bullet points
- If asks for "brief" or "short" → 3-4 bullets
- If asks for "key insight" or "key idea" → 1-2 bullets with most important points
- Default (no length specified) → 4-5 bullets

DOCUMENT:
{document_text}

USER QUERY:
{user_query}

Summary (respect length requirement from USER QUERY):
"""
ENTITY_PROMPT = """
You extract entities from a document based on the user's request.

RULES:
1. Extract ONLY what the user asked for. If they ask for "organizations only" or "names" or "extract names", output ONLY those types. Ignore any other instructions in the same request.
2. If the user asks for "all entities" or "extract entities" without specifying types, extract common meaningful types explicitly present: People/Names, Organizations, Dates, Locations, Amounts, etc. Use plural, title-case labels.
3. Extract ONLY values that appear verbatim or very closely in the document. Do NOT invent or infer.
4. If a requested entity type has no matches in the document, omit that label.
5. Do NOT add labels or values not explicitly in the document.

OUTPUT FORMAT (strict, one label per line):
Label = [item1, item2]

Each label on its own line. Use comma-separated values inside brackets.

DOCUMENT:
{document_text}

USER REQUEST:
{user_query}

Output (Label = [item1, item2] format only):
"""

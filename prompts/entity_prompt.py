ENTITY_PROMPT = """
Extract ONLY the entities specifically requested.

RULES:
1. Look at the USER REQUEST below
2. Find which entity types are mentioned (e.g., "animals", "books", "dates", "people")
3. Extract ONLY those types - NOTHING ELSE
4. Output format: EntityType: [item1, item2]
5. Do NOT extract types that weren't requested

DOCUMENT:
{document_text}

USER REQUEST:
{user_query}

Examples:
- Request: "list animals" → Output: Animals: [Rex, Bruno]
- Request: "extract books and dates" → Output: Books: [...], Dates: [...]
- Request: "show people" → Output: People: [...]

NOW extract ONLY what was requested in USER REQUEST above:
"""
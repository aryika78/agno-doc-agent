import re
from tools.entity_tool import entity_finder_tool


class ExtractionAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text

    def extract_entities(self, user_query: str):
        raw = entity_finder_tool(self.document_text, user_query)

        # Case 1: Tool already returned structured entities
        if isinstance(raw, dict) and "entities" in raw:
            return raw

        # Case 2: Tool returned plain text → parse into structured dict
        if isinstance(raw, str):
            entities = {}
            pattern = r"(\w+):\s*\[([^\]]*)\]"

            for key, values in re.findall(pattern, raw):
                entities[key] = [
                    v.strip()
                    for v in re.split(r",(?!\d)", values)
                    if v.strip()
                ]

            return {"entities": entities}

        # Case 3: Tool returned a flat list → normalize
        if isinstance(raw, list):
            return {"entities": {"Items": raw}}

        # Absolute fallback (never break the pipeline)
        return {"entities": {}}

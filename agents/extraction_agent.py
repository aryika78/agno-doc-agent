import re
from tools.entity_tool import entity_finder_tool


class ExtractionAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text

    def _item_in_document(self, item: str, text: str) -> bool:
        """Check if item appears in document (case-insensitive substring) to prevent hallucination."""
        if not item or not text:
            return False
        return item.strip().lower() in text.lower()

    def extract_entities(self, user_query: str):
        text = self.document_text
        if not text or not text.strip():
            return {"entities": {}}

        raw = entity_finder_tool(text, user_query)

        labelled = {}
        if isinstance(raw, str) and raw.strip():
            for label, values in re.findall(r"([A-Za-z ]+)\s*=\s*\[(.*?)\]", raw):
                items = [v.strip() for v in values.split(",") if v.strip()]
                # Keep only items that appear in the document
                validated = [x for x in items if self._item_in_document(x, text)]
                if validated:
                    labelled[label.strip()] = validated

        return {"entities": labelled}

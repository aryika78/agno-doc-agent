import re
from tools.agno_tools import extract_entities_from_document


class ExtractionAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text

    def _item_in_document(self, item: str, text: str) -> bool:
        """Check if item appears in document (case-insensitive substring) to prevent hallucination."""
        if not item or not text:
            return False
        return item.strip().lower() in text.lower()

    def _strip_quotes(self, s: str) -> str:
        """Strip surrounding quotes only if both ends match."""
        s = s.strip()
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            return s[1:-1]
        if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
            return s[1:-1]
        return s

    def extract_entities(self, user_query: str):
        text = self.document_text
        if not text or not text.strip():
            return {"entities": {}}

        raw = extract_entities_from_document(text, user_query)

        labelled = {}
        if isinstance(raw, str) and raw.strip():
            for label, values in re.findall(r"([A-Za-z ]+)\s*=\s*\[(.*?)\]", raw):
                items = [v.strip() for v in values.split(",") if v.strip()]
                # Keep only items that appear in the document, strip surrounding quotes for clean output
                validated = [
                    self._strip_quotes(x) for x in items
                    if self._item_in_document(x, text)
                ]
                if validated:
                    labelled[label.strip()] = validated

        return {"entities": labelled}

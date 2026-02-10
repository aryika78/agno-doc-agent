import re
from tools.entity_tool import entity_finder_tool


class ExtractionAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text

    def extract_entities(self, user_query: str):
        q = user_query.lower()
        text = self.document_text

        # --------------------------------------------------
        # 1. DOCUMENT-FIRST ENTITY CANDIDATES (SAFE)
        # --------------------------------------------------
        candidates = set()

        # Multi-word proper nouns / titles / names
        candidates.update(
            re.findall(
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z0-9]+)+\b",
                text
            )
        )

        # Dates like "January 1, 2024"
        candidates.update(
            re.findall(
                r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
                text
            )
        )

        # Quantities with context
        candidates.update(
            re.findall(
                r"\b\d+\s+(?:days?|weeks?|months?|years?|hours?|%)\b",
                text,
                flags=re.IGNORECASE
            )
        )

        # Quoted entities (books, titles, names)
        candidates.update(
            re.findall(r"['\"]([^'\"]+)['\"]", text)
        )

        candidates = sorted(c.strip() for c in candidates if len(c.strip()) > 2)

        if not candidates:
            return {"entities": {}}

        # --------------------------------------------------
        # 2. LLM = LABEL ONLY (NOT DECISION MAKER)
        # --------------------------------------------------
        labeling_prompt = (
            "You are an entity labeling system.\n"
            "Entities were already extracted from a document.\n\n"
            "RULES:\n"
            "- Do NOT invent entities\n"
            "- Do NOT remove entities\n"
            "- ONLY group and label them\n"
            "- Use plural, title-case labels\n\n"
            "ENTITIES:\n"
            + "\n".join(candidates)
            + "\n\n"
            "OUTPUT FORMAT:\n"
            "Label = [item1, item2]\n"
        )

        # ✅ FIXED CALL (THIS WAS THE MAIN BUG)
        raw = entity_finder_tool(candidates, "label entities")

        labelled = {}

        if isinstance(raw, str) and raw.strip():
            for label, values in re.findall(r"([A-Za-z ]+)\s*=\s*\[(.*?)\]", raw):
                items = [
                    v.strip()
                    for v in values.split(",")
                    if v.strip() in candidates
                ]
                if items:
                    labelled[label.strip()] = items

        # --------------------------------------------------
        # 3. SAFE FALLBACK (LABEL-AGNOSTIC)
        # --------------------------------------------------
        if not labelled:
            labelled = {"Uncategorized Entities": candidates}

        # --------------------------------------------------
        # 4. QUERY-AWARE FILTERING
        # --------------------------------------------------
        if "all" not in q:
            filtered = {
                label: items
                for label, items in labelled.items()
                if any(word in q for word in label.lower().split())
            }
            labelled = filtered or labelled

        return {"entities": labelled}

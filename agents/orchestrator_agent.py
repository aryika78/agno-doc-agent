from agents.document_analyst_agent import DocumentAnalystAgent
from agents.extraction_agent import ExtractionAgent
from agents.response_composer_agent import ResponseComposerAgent
import re


class OrchestratorAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.analyst = DocumentAnalystAgent(document_text)
        self.extractor = ExtractionAgent(document_text)
        self.composer = ResponseComposerAgent()

    def normalize_query(self, user_query: str) -> str:
        q = user_query.lower()
        replacements = {
            "extrat": "extract", "exract": "extract", "summarise": "summarize",
            "locaton": "location", "thsi": "this", "eho": "who",
            "sighned": "signed", "shoe": "show", "amd": "and",
            "animls": "animals", "boks": "books",
            "deadlin": "deadline", "giv": "give", "summry": "summary",
            "explan": "explain",
        }
        for wrong, correct in replacements.items():
            q = q.replace(wrong, correct)
        return q

    def split_into_intent_chunks(self, query: str) -> list[str]:
        pattern = r"\b(then|also|next)\b"
        chunks = re.split(pattern, query)

        clean_chunks = []
        buffer = ""

        for part in chunks:
            part = part.strip()
            if part in ["then", "also", "next"]:
                if buffer:
                    clean_chunks.append(buffer.strip())
                buffer = ""
            else:
                buffer += " " + part

        if buffer.strip():
            clean_chunks.append(buffer.strip())

        return clean_chunks

    def classify_intent(self, user_query: str) -> list[tuple[str, str]]:
        q = self.normalize_query(user_query)
        parts = self.split_into_intent_chunks(q)

        tasks = []

        for part in parts:
            if not part:
                continue

            if any(w in part for w in ["summarize", "summary", "key insight", "key idea"]):
                tasks.append(("summary", part))

            if any(w in part for w in ["extract", "list", "show", "find"]):
                tasks.append(("entities", part))

            if not tasks:
                tasks.append(("qa", part))

        return tasks

    def handle(self, user_query: str) -> list[dict]:
        normalized_query = self.normalize_query(user_query)
        json_mode = "json" in normalized_query

        tasks = self.classify_intent(user_query)
        tasks.sort(key=lambda x: 0 if x[0] == "summary" else 1)

        json_output = {}
        outputs = []

        for intent, query_part in tasks:

            if intent == "summary":
                summary = self.analyst.summarize(query_part)
                if json_mode:
                    json_output["summary"] = summary
                else:
                    outputs.append(summary)

            elif intent == "entities":
                result = self.extractor.extract_entities(query_part)["entities"]

                if json_mode:
                    json_output.update(result)
                else:
                    lowered = query_part.lower()
                    lines = []
                    for k, v in result.items():
                        if k.lower() in lowered or not any(word in lowered for word in result.keys()):
                            lines.append(f"{k} = [{', '.join(v)}]")

                    outputs.append("\n\n".join(lines))

            elif intent == "qa" and not json_mode:
                outputs.append(self.analyst.answer(query_part))

        # 🔒 HARD GUARANTEE: NEVER RETURN None
        if json_mode:
            return self.composer.compose([json_output])

        return self.composer.compose(outputs or [])

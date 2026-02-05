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

    # ✅ Split only on real task separators
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

    # ✅ TRUE multi-intent detection
    def classify_intent(self, user_query: str) -> list[tuple[str, str]]:
        q = self.normalize_query(user_query)
        parts = self.split_into_intent_chunks(q)

        tasks = []

        for part in parts:
            if not part:
                continue

            part_tasks = []

            # JSON
            if "json" in part:
                part_tasks.append(("json", part))

            # QA (question words anywhere)
            if any(word in part for word in ["what", "who", "where", "when", "why", "how"]):
                part_tasks.append(("qa", part))

            # Summary
            if any(word in part for word in ["summarize", "summary", "key insight", "key idea"]):
                part_tasks.append(("summary", part))

            # Entities (ONLY if JSON not requested)
            if "json" not in part and any(word in part for word in ["extract", "list", "show", "find"]):
                part_tasks.append(("entities", part))

            # Fallback
            if not part_tasks:
                part_tasks.append(("qa", part))

            tasks.extend(part_tasks)

        return tasks

    def handle(self, user_query: str) -> str:
        outputs = []
        tasks = self.classify_intent(user_query)

        print(f"\n[Intent Flow]: {' → '.join([i for i, _ in tasks])}")

        for intent, query_part in tasks:

            # 🔴 Priority control
            intents_in_same_part = [i for i, p in tasks if p == query_part]

            # If JSON exists for this part → run ONLY json
            if "json" in intents_in_same_part and intent != "json":
                continue

            # If Summary exists → skip QA
            if "summary" in intents_in_same_part and intent == "qa":
                continue

            # If QA exists → skip Entities
            if "qa" in intents_in_same_part and intent == "entities":
                continue

            # 🔹 Execute
            if intent == "qa":
                outputs.append(self.analyst.answer(query_part))
            elif intent == "summary":
                outputs.append(self.analyst.summarize(query_part))
            elif intent == "entities":
                outputs.append(self.extractor.extract_entities(query_part))
            elif intent == "json":
                outputs.append(self.extractor.extract_json(query_part))

        return self.composer.compose(outputs)


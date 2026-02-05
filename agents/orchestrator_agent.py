from agents.document_analyst_agent import DocumentAnalystAgent
from agents.extraction_agent import ExtractionAgent
from agents.response_composer_agent import ResponseComposerAgent
from prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from azure_client import client, DEPLOYMENT_REASONING


class OrchestratorAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.analyst = DocumentAnalystAgent(document_text)
        self.extractor = ExtractionAgent(document_text)
        self.composer = ResponseComposerAgent()
    
    def normalize_query(self, user_query: str) -> str:
        q = user_query.lower()
        replacements = {
            "extrat": "extract",
            "exract": "extract",
            "summarise": "summarize",
            "locaton": "location",
            "thsi": "this",
            "eho": "who",
            "sighned": "signed",
            "shoe": "show",
        }
        for wrong, correct in replacements.items():
            q = q.replace(wrong, correct)
        return q

    def classify_intent(self, user_query: str) -> list[str]:
        # Normalize first (handles typos like exract, extrat, etc.)
        q = self.normalize_query(user_query).lower()

        # 🔒 Special rule: if user wants entities in JSON → JSON only
        if "json" in q and ("entities" in q or "extract" in q):
            return ["json"]

        # 🔒 Rule: list-style questions are entities, not QA
        list_patterns = [
            "who are", "what are", "names of", "list of",
            "people mentioned", "locations mentioned",
            "books mentioned", "dates mentioned",
            "show all", "provide names", "every date", "all books"
        ]

        if any(p in q for p in list_patterns):
            return ["entities"]

        # 🔒 Direct keyword rules (avoid LLM confusion)
        if "summarize" in q or "summary" in q:
            return ["summary"]

        if "json" in q:
            return ["json"]

        # Otherwise let LLM classify intent
        prompt = ORCHESTRATOR_PROMPT.format(user_query=user_query)

        response = client.chat.completions.create(
            model=DEPLOYMENT_REASONING,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        intents = response.choices[0].message.content.strip().lower()
        return [i.strip() for i in intents.split(",")]



    def handle(self, user_query: str) -> str:
        outputs = []
        intents = self.classify_intent(user_query)

        for intent in intents:

            if intent == "summary":
                outputs.append(self.analyst.summarize(user_query))

            elif intent == "qa":
                outputs.append(self.analyst.answer(user_query))

            elif intent == "entities":
                outputs.append(self.extractor.extract_entities(user_query))

            elif intent == "json":
                outputs.append(self.extractor.extract_json())

        return self.composer.compose(outputs)

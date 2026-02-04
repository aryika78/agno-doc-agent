from agents.document_analyst_agent import DocumentAnalystAgent
from agents.extraction_agent import ExtractionAgent
from agents.response_composer_agent import ResponseComposerAgent


class OrchestratorAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.analyst = DocumentAnalystAgent(document_text)
        self.extractor = ExtractionAgent(document_text)
        self.composer = ResponseComposerAgent()

    def handle(self, user_query: str) -> str:
        outputs = []
        q = user_query.lower()

        if "summarize" in q or "summary" in q:
            outputs.append(self.analyst.summarize(user_query))

        elif "what" in q or "who" in q or "where" in q:
            outputs.append(self.analyst.answer(user_query))

        if "extract" in q or "entities" in q:
            outputs.append(self.extractor.extract_entities(user_query))

        if "json" in q:
            outputs.append(self.extractor.extract_json())

        return self.composer.compose(outputs)

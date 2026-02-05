from agents.document_analyst_agent import DocumentAnalystAgent
from agents.extraction_agent import ExtractionAgent
from agents.response_composer_agent import ResponseComposerAgent


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
            "the": "then", "animls": "animals", "boks": "books",
            "deadlin": "deadline", "giv": "give", "summry": "summary",
            "explan": "explain",
        }
        for wrong, correct in replacements.items():
            q = q.replace(wrong, correct)
        return q

    def classify_intent(self, user_query: str) -> list[tuple[str, str]]:
        """Returns list of (intent, relevant_query_part) tuples"""
        q = self.normalize_query(user_query).lower()
        
        # Split by "then" to get sequential tasks
        parts = [p.strip() for p in q.split("then")]
        tasks = []
        
        for part in parts:
            # CHECK JSON FIRST (before entities check)
            if "json" in part:
                tasks.append(("json", part))
            
            # Detect intent for each part
            elif any(word in part for word in ["extract", "list", "show all", "give all", "provide"]):
                tasks.append(("entities", part))
            
            elif any(word in part for word in ["explain", "what do", "what does", "describe"]):
                tasks.append(("qa", part))
            
            elif any(word in part for word in ["summarize", "summary", "key insight", "key idea"]):
                tasks.append(("summary", part))
        
        # If no tasks found, treat as QA
        if not tasks:
            tasks = [("qa", user_query)]
        
        return tasks

    def handle(self, user_query: str) -> str:
        outputs = []
        tasks = self.classify_intent(user_query)

        for intent, query_part in tasks:
            if intent == "qa":
                outputs.append(self.analyst.answer(query_part))
            elif intent == "summary":
                outputs.append(self.analyst.summarize(query_part))
            elif intent == "entities":
                outputs.append(self.extractor.extract_entities(query_part))
            elif intent == "json":
                outputs.append(self.extractor.extract_json())

        return self.composer.compose(outputs)
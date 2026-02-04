from tools.entity_tool import entity_finder_tool
from tools.json_tool import json_extractor_tool


class ExtractionAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text

    def extract_entities(self, user_query: str):
        return entity_finder_tool(self.document_text, user_query)

    def extract_json(self):
        return json_extractor_tool(self.document_text)

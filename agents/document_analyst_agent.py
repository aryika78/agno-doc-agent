from tools.classifier_tool import doc_classifier_tool
from tools.summary_tool import smart_summary_tool
from tools.qa_tool import qa_from_doc_tool


class DocumentAnalystAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.doc_type = None

    def classify(self):
        self.doc_type = doc_classifier_tool(self.document_text)
        return self.doc_type

    def summarize(self, user_query: str):
        return smart_summary_tool(self.document_text, user_query)

    def answer(self, user_query: str):
        return qa_from_doc_tool(self.document_text, user_query)

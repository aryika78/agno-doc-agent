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
        """
        STRICT SUMMARY ONLY.
        - No entities
        - No JSON
        - No lists
        - No headings
        - No formatting
        """
        strict_query = (
            "Summarize the document clearly and concisely.\n\n"
            "STRICT RULES:\n"
            "- Output ONLY plain summary text\n"
            "- DO NOT include entities\n"
            "- DO NOT include JSON\n"
            "- DO NOT include headings or labels\n"
            "- DO NOT include bullet points\n\n"
            f"{self.document_text}"
        )

        summary = smart_summary_tool(self.document_text, strict_query)

        # 🔒 HARD SAFETY: force plain text
        if not isinstance(summary, str):
            summary = str(summary)

        # Strip accidental markdown / code blocks
        summary = summary.replace("```", "").strip()

        return summary

    def answer(self, user_query: str):
        """
        QA ONLY.
        Never return JSON.
        """
        answer = qa_from_doc_tool(self.document_text, user_query)

        if not isinstance(answer, str):
            answer = str(answer)

        return answer.strip()

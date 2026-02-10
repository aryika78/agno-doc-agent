from tools.classifier_tool import doc_classifier_tool
from tools.summary_tool import smart_summary_tool
from tools.qa_tool import qa_from_doc_tool
from prompts.summary_prompt import SUMMARY_PROMPT
import re


class DocumentAnalystAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.doc_type = None

    def classify(self):
        self.doc_type = doc_classifier_tool(self.document_text)
        return self.doc_type

    def _normalize_text(self, text: str) -> str:
        # Join broken lines safely
        text = re.sub(r"\n(?=[a-zA-Z])", " ", text)
        return text.strip()

    def _split_sentences(self, text: str) -> list[str]:
        """
        Split sentences ONLY on real sentence boundaries.
        Safe for:
        - Mr. / Dr. / Inc.
        - ASP.NET / Node.js / .NET
        - Decimal numbers
        """
        text = self._normalize_text(text)

        # Split on punctuation followed by space + Capital letter
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

        return [p.strip() for p in parts if p.strip()]

    def summarize(self, user_query: str):
        query_lower = user_query.lower()

        # ---- ROUTE INSIGHT / IDEA QUESTIONS TO QA ----
        INSIGHT_TRIGGERS = [
            "key insight",
            "key idea",
            "main idea",
            "what is this document about",
            "overall idea",
        ]

        if any(t in query_lower for t in INSIGHT_TRIGGERS):
            answer = qa_from_doc_tool(self.document_text, user_query)
            return str(answer).strip()

        # ---- detect count ----
        count = None
        m = re.search(r"(\d+)\s*(lines|line|points|bullets)", query_lower)
        if m:
            count = int(m.group(1))

        wants_points = any(
            w in query_lower for w in ["point", "points", "bullet", "bullets", "list"]
        )

        # ---- RAW FACTS FROM LLM ----
        raw = smart_summary_tool(
            self.document_text,
            SUMMARY_PROMPT.format(document_text=self.document_text)
        )

        if not isinstance(raw, str):
            raw = str(raw)

        sentences = self._split_sentences(raw)

        # Enforce count WITHOUT hallucination
        if count:
            sentences = sentences[:count]

        if wants_points:
            return "\n".join(f"- {s}" for s in sentences)

        return " ".join(sentences)

    def answer(self, user_query: str):
        """
        QA ONLY.
        Never return JSON.
        """
        answer = qa_from_doc_tool(self.document_text, user_query)

        if not isinstance(answer, str):
            answer = str(answer)

        return answer.strip()

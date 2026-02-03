from tools.summary_tool import smart_summary_tool
from tools.json_tool import json_extractor_tool
from tools.entity_tool import entity_finder_tool
from tools.qa_tool import qa_from_doc_tool
from tools.classifier_tool import doc_classifier_tool


def route_query(user_query: str, document_text: str) -> str:
    q = user_query.lower()

    if "summary" in q or "summarize" in q:
        return smart_summary_tool(document_text)

    elif "json" in q or "extract" in q:
        return json_extractor_tool(document_text)

    elif "date" in q or "people" in q or "money" in q or "deadline" in q:
        return entity_finder_tool(document_text, user_query)

    elif "classify" in q or "type" in q:
        return doc_classifier_tool(document_text)

    else:
        return qa_from_doc_tool(document_text, user_query)

from tools.summary_tool import smart_summary_tool
from tools.json_tool import json_extractor_tool
from tools.entity_tool import entity_finder_tool
from tools.qa_tool import qa_from_doc_tool
from tools.classifier_tool import doc_classifier_tool
from router_llm import llm_router

def route_query(user_query: str, document_text: str) -> str:
    tool = llm_router(user_query)
    print(f"\n[ROUTER CHOSE]: {tool}\n")   # 👈 ADD THIS LINE

    if tool == "summary_tool":
        return smart_summary_tool(document_text, user_query)

    elif tool == "json_tool":
        return json_extractor_tool(document_text)

    elif tool == "entity_tool":
        return entity_finder_tool(document_text, user_query)

    elif tool == "classifier_tool":
        return doc_classifier_tool(document_text)

    else:
        return qa_from_doc_tool(document_text, user_query)


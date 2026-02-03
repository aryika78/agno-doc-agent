from agno.agent import Agent
from agno.tools import tool

from tools.summary_tool import smart_summary_tool
from tools.json_tool import json_extractor_tool
from tools.entity_tool import entity_finder_tool
from tools.qa_tool import qa_from_doc_tool
from tools.classifier_tool import doc_classifier_tool


@tool
def summary_tool(document_text: str) -> str:
    """Use this tool to create a bullet summary of the document."""
    return smart_summary_tool(document_text)


@tool
def json_tool(document_text: str) -> str:
    """Use this tool to extract structured JSON from the document."""
    return json_extractor_tool(document_text)


@tool
def entity_tool(document_text: str) -> str:
    """Use this tool to find dates, people, money, and deadlines."""
    return entity_finder_tool(document_text)


@tool
def qa_tool(document_text: str, user_query: str) -> str:
    """Use this tool to answer questions strictly from the document."""
    return qa_from_doc_tool(document_text, user_query)


@tool
def classifier_tool(document_text: str) -> str:
    """Use this tool to classify the document type."""
    return doc_classifier_tool(document_text)


agent = Agent(
    tools=[summary_tool, json_tool, entity_tool, qa_tool, classifier_tool]
)

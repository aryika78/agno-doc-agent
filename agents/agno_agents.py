"""
Agno Agent for document processing.
Single agent handles QA, summarization, entity extraction, and visualizations.
The LLM decides how to respond and which tools to use based on the user's query.
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools import tool
from prompts.agent_prompt import AGENT_INSTRUCTIONS

load_dotenv()

_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
_AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
_API_VERSION = "2024-02-01"
_DEPLOYMENT_REASONING = os.getenv("DEPLOYMENT_REASONING", "gpt-5-nano")


def _build_model():
    return AzureOpenAI(
        id=_DEPLOYMENT_REASONING,
        azure_endpoint=_AZURE_ENDPOINT,
        azure_deployment=_DEPLOYMENT_REASONING,
        api_key=_API_KEY,
        api_version=_API_VERSION,
    )


def create_document_agent() -> Agent:
    """Create a basic agent (no tools) for utility calls like suggested questions, insights, follow-ups."""
    return Agent(
        name="Document Agent",
        model=_build_model(),
        instructions=[AGENT_INSTRUCTIONS],
        markdown=True,
    )


def create_tool_agent(doc_id: str, store) -> Agent:
    """Create an agentic document agent with retrieval tools. The agent decides what context to fetch."""

    @tool(description="Search the document for text passages relevant to a query. Use this for specific questions about particular topics, people, dates, or facts.")
    def search_document(query: str) -> str:
        result = store.search(query=query, doc_id=doc_id, top_k=10)
        return result if result else "No relevant content found."

    @tool(description="Get the full document text. Use this for broad questions like summaries, overviews, or when you need to see the complete document.")
    def get_full_text() -> str:
        result = store.get_full_text(doc_id)
        return result if result else "Document is empty."

    return Agent(
        name="Document Agent",
        model=_build_model(),
        instructions=[AGENT_INSTRUCTIONS],
        tools=[search_document, get_full_text],
        markdown=True,
    )

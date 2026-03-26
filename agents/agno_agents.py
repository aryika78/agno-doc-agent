"""
Agno Agent for document processing.
Single agent handles QA, summarization, and entity extraction.
The LLM decides how to respond based on the user's query.
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from prompts.agent_prompt import AGENT_INSTRUCTIONS

load_dotenv()

_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
_AZURE_ENDPOINT = "https://vanshavali-ai-resource.cognitiveservices.azure.com"
_API_VERSION = "2024-02-01"
_DEPLOYMENT_REASONING = os.getenv("DEPLOYMENT_REASONING", "gpt-5-nano")


def create_document_agent() -> Agent:
    """Create and return the document processing Agent."""
    return Agent(
        name="Document Agent",
        model=AzureOpenAI(
            id=_DEPLOYMENT_REASONING,
            azure_endpoint=_AZURE_ENDPOINT,
            azure_deployment=_DEPLOYMENT_REASONING,
            api_key=_API_KEY,
            api_version=_API_VERSION,
        ),
        instructions=[AGENT_INSTRUCTIONS],
        markdown=True,
    )

"""
Agno tools for document QA, summary, and entity extraction.
Plain callable functions - Agents accept these as tools.
"""
import os
from prompts.qa_prompt import QA_PROMPT
from prompts.summary_prompt import SUMMARY_PROMPT
from prompts.entity_prompt import ENTITY_PROMPT
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
_DEPLOYMENT_REASONING = os.getenv("DEPLOYMENT_REASONING")
_DEPLOYMENT_SUMMARY = os.getenv("DEPLOYMENT_SUMMARY")


def _call_llm(prompt: str, deployment: str) -> str:
    response = _client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content


def qa_from_document(document_text: str, user_query: str) -> str:
    """Answer the user's question based on the document text."""
    prompt = QA_PROMPT.format(
        document_text=document_text.strip(),
        user_query=user_query.strip(),
    )
    return _call_llm(prompt, _DEPLOYMENT_REASONING)


def summarize_document(document_text: str, user_query: str) -> str:
    """Summarize the document according to the user's request."""
    prompt = SUMMARY_PROMPT.format(
        document_text=document_text.strip(),
        user_query=user_query.strip(),
    )
    return _call_llm(prompt, _DEPLOYMENT_SUMMARY)


def extract_entities_from_document(document_text: str, user_query: str) -> str:
    """Extract entities from the document based on the user's request. Output format: Label = [item1, item2]"""
    prompt = ENTITY_PROMPT.format(
        document_text=document_text.strip(),
        user_query=user_query.strip(),
    )
    return _call_llm(prompt, _DEPLOYMENT_REASONING)

"""
Agno Agent instances for QA, Summary, and Entity extraction.
Orchestrator calls tools directly; Agents provide structure.
"""
import os
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from tools.agno_tools import (
    qa_from_document,
    summarize_document,
    extract_entities_from_document,
)

_DEPLOYMENT_REASONING = os.getenv("DEPLOYMENT_REASONING")
_DEPLOYMENT_SUMMARY = os.getenv("DEPLOYMENT_SUMMARY")

QA_AGENT = Agent(
    model=AzureOpenAI(id=_DEPLOYMENT_REASONING),
    tools=[qa_from_document],
    description="Answers questions about documents",
)

SUMMARY_AGENT = Agent(
    model=AzureOpenAI(id=_DEPLOYMENT_SUMMARY),
    tools=[summarize_document],
    description="Summarizes documents based on user request",
)

ENTITY_AGENT = Agent(
    model=AzureOpenAI(id=_DEPLOYMENT_REASONING),
    tools=[extract_entities_from_document],
    description="Extracts entities from documents",
)

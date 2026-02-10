import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Model deployments
DEPLOYMENT_CLASSIFIER = os.getenv("DEPLOYMENT_CLASSIFIER")      # 4.1-nano
DEPLOYMENT_SUMMARY = os.getenv("DEPLOYMENT_SUMMARY")            # 4.1-nano
DEPLOYMENT_REASONING = os.getenv("DEPLOYMENT_REASONING")        # 5-nano
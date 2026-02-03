from openai import AzureOpenAI
from prompts.entity_prompt import ENTITY_PROMPT
from azure_client import client, DEPLOYMENT_NAME
client = AzureOpenAI(
    api_key="YOUR_AZURE_KEY",
    api_version="2024-02-15-preview",
    azure_endpoint="https://YOUR-RESOURCE.openai.azure.com/"
)

def entity_finder_tool(document_text: str) -> str:
    prompt = ENTITY_PROMPT.format(document_text=document_text)

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

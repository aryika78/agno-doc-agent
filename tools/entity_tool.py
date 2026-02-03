from openai import AzureOpenAI
from prompts.entity_prompt import ENTITY_PROMPT
from azure_client import client, DEPLOYMENT_NAME

def entity_finder_tool(document_text: str) -> str:
    prompt = ENTITY_PROMPT.format(document_text=document_text)

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

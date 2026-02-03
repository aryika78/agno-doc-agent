from openai import AzureOpenAI
from prompts.qa_prompt import QA_PROMPT
from azure_client import client, DEPLOYMENT_NAME
client = AzureOpenAI(
    api_key="YOUR_AZURE_KEY",
    api_version="2024-02-15-preview",
    azure_endpoint="https://YOUR-RESOURCE.openai.azure.com/"
)

def qa_from_doc_tool(document_text: str, user_query: str) -> str:
    prompt = QA_PROMPT.format(
        document_text=document_text,
        user_query=user_query
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

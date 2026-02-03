from openai import AzureOpenAI
from prompts.classifier_prompt import CLASSIFIER_PROMPT

client = AzureOpenAI(
    api_key="YOUR_AZURE_KEY",
    api_version="2024-02-15-preview",
    azure_endpoint="https://YOUR-RESOURCE.openai.azure.com/"
)

def doc_classifier_tool(document_text: str) -> str:
    prompt = CLASSIFIER_PROMPT.format(document_text=document_text)

    response = client.chat.completions.create(
        model="YOUR_DEPLOYMENT_NAME",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

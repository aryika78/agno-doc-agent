from openai import AzureOpenAI
from prompts.classifier_prompt import CLASSIFIER_PROMPT
from azure_client import client, DEPLOYMENT_CLASSIFIER

def doc_classifier_tool(document_text: str) -> str:
    prompt = CLASSIFIER_PROMPT.format(document_text=document_text.strip())


    response = client.chat.completions.create(
        model=DEPLOYMENT_CLASSIFIER,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

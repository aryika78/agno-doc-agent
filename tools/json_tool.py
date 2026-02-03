from openai import AzureOpenAI
from prompts.json_prompt import JSON_PROMPT

client = AzureOpenAI(
    api_key="YOUR_AZURE_KEY",
    api_version="2024-02-15-preview",
    azure_endpoint="https://YOUR-RESOURCE.openai.azure.com/"
)

def json_extractor_tool(document_text: str) -> str:
    prompt = JSON_PROMPT.format(document_text=document_text)

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

from openai import AzureOpenAI
from prompts.summary_prompt import SUMMARY_PROMPT
from azure_client import client, DEPLOYMENT_SUMMARY

def smart_summary_tool(document_text: str) -> str:
    prompt = SUMMARY_PROMPT.format(document_text=document_text.strip())

    response = client.chat.completions.create(
        model=DEPLOYMENT_SUMMARY,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

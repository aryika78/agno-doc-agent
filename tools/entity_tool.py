from prompts.entity_prompt import ENTITY_PROMPT
from azure_client import client, DEPLOYMENT_NAME

def entity_finder_tool(document_text: str, user_query: str) -> str:
    prompt = ENTITY_PROMPT.format(
        document_text=document_text,
        user_query=user_query
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

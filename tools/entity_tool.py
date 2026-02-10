from prompts.entity_prompt import ENTITY_PROMPT
from azure_client import client, DEPLOYMENT_REASONING


def entity_finder_tool(document_text: str, user_query: str) -> str:
    prompt = ENTITY_PROMPT.format(
        document_text=document_text.strip(),
        user_query=user_query.strip()
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_REASONING,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

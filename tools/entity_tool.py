from prompts.entity_prompt import ENTITY_PROMPT
from azure_client import client, DEPLOYMENT_REASONING

def entity_finder_tool(entities: list[str], user_query: str) -> str:
    prompt = ENTITY_PROMPT.format(
        entities="\n".join(entities)
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_REASONING,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

from azure_client import client, DEPLOYMENT_REASONING
from prompts.router_prompt import ROUTER_PROMPT

def llm_router(user_query: str) -> str:
    prompt = ROUTER_PROMPT.format(user_query=user_query.strip())

    response = client.chat.completions.create(
        model=DEPLOYMENT_REASONING,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()

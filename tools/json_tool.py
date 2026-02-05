from prompts.json_prompt import JSON_PROMPT
from azure_client import client, DEPLOYMENT_REASONING


def json_extractor_tool(document_text: str, user_query: str) -> str:
    prompt = JSON_PROMPT.format(
        document_text=document_text.strip(),
        user_query=user_query.strip()
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_REASONING,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

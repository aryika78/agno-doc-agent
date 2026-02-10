ENTITY_PROMPT = """
You are an entity labeling system.

You will be given a list of entities that were already extracted.

RULES:
- Do NOT invent new entities.
- Do NOT remove any entities.
- Your ONLY task is to GROUP and LABEL the given entities.
- Use meaningful, plural, title-case labels.
- Create a new label whenever appropriate.
- If unsure, choose the best reasonable label.
- NEVER return an empty response.

OUTPUT FORMAT (STRICT):
Label = [item1, item2]

Each label must be on its own line.

ENTITIES:
{entities}

"""

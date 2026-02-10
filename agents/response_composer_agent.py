import json

class ResponseComposerAgent:
    def compose(self, parts: list) -> list[dict]:
        blocks = []

        for part in parts:
            if isinstance(part, dict):
                blocks.append({
                    "type": "json",
                    "content": part
                })

            elif isinstance(part, str):
                blocks.append({
                    "type": "text",
                    "content": part
                })

            elif isinstance(part, list):
                blocks.append({
                    "type": "text",
                    "content": "\n".join(part)
                })

            else:
                blocks.append({
                    "type": "text",
                    "content": str(part)
                })

        return blocks

import json

class ResponseComposerAgent:
    def compose(self, parts: list) -> list[dict]:
        blocks = []

        for part in parts:

            # ✅ JSON mode (prettify button works)
            if isinstance(part, dict):
                blocks.append({
                    "type": "json",
                    "content": part
                })

            # ✅ Plain grouped entity text (already formatted)
            elif isinstance(part, str):
                blocks.append({
                    "type": "text",
                    "content": part
                })

            # ✅ Safety: list → join as plain text
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

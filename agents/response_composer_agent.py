import json
class ResponseComposerAgent:
    def compose(self, parts: list[str]) -> list[dict]:
        blocks = []
        has_json = False

        # First pass: detect JSON blocks
        for part in parts:
            part = part.strip()
            if part.startswith("{") and part.endswith("}"):
                try:
                    json.loads(part)
                    blocks.append({"type": "json", "content": part})
                    has_json = True
                    continue
                except Exception:
                    pass

            blocks.append({"type": "text", "content": part})

        # 🔥 SECOND PASS FIX
        if has_json:
            blocks = [
                b for b in blocks
                if not (
                    b["type"] == "text"
                    and b["content"].strip().startswith("{")
                    and b["content"].strip().endswith("}")
                )
            ]

        return blocks

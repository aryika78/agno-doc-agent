import json
import re


class ResponseComposerAgent:
    def compose(self, parts: list[str]) -> str:
        """
        Intelligently combine outputs from multiple agents into
        a clean, non-repetitive response.
        """

        text_blocks = []
        json_blocks = []
        list_blocks = []

        for part in parts:
            part = part.strip()

            # ✅ JSON detection
            if part.startswith("{") and part.endswith("}"):
                try:
                    json_obj = json.loads(part)
                    json_blocks.append(json.dumps(json_obj, indent=2))
                except Exception:
                    text_blocks.append(part)

            elif re.search(r"\w+:\s*\[.*\]", part):
                # Force split between entity groups even if model returned one line
                forced_lines = re.findall(r"\w+:\s*\[[^\]]*\]", part)
                list_blocks.extend(forced_lines)

            # ✅ Normal sentences (QA / Summary)
            else:
                text_blocks.append(part)

        final_response = []

        # 1️⃣ Main answers / summaries first
        if text_blocks:
            # Remove duplicates while preserving order
            seen = set()
            clean_text = []
            for t in text_blocks:
                if t not in seen:
                    clean_text.append(t)
                    seen.add(t)
            final_response.append("\n".join(clean_text))

        # 2️⃣ Lists (entities) — group by label and add spacing
        if list_blocks and not json_blocks:
            grouped = {}

            for line in list_blocks:
                label, values = line.split(":", 1)
                label = label.strip()
                values = values.strip()

                grouped.setdefault(label, []).append(values)

            formatted_lists = []
            for label, vals in grouped.items():
                joined_vals = ", ".join(vals)
                formatted_lists.append(f"{label}: {joined_vals}")

            final_response.append("\n\n".join(formatted_lists))

        # 3️⃣ JSON at the end
        if json_blocks:
            final_response.append("\n\n".join(json_blocks))

        return "\n\n".join(final_response)

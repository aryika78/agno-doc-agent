class ResponseComposerAgent:
    def compose(self, parts: list[str]) -> str:
        """
        Combine multiple agent outputs into a single response.
        """
        return "\n\n".join(parts)

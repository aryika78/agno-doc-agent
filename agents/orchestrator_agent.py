from agents.document_analyst_agent import DocumentAnalystAgent
from agents.extraction_agent import ExtractionAgent
from agents.response_composer_agent import ResponseComposerAgent
from agents.agno_agents import QA_AGENT, SUMMARY_AGENT, ENTITY_AGENT  # Agno structure
import json
import re


class OrchestratorAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.analyst = DocumentAnalystAgent(document_text)
        self.extractor = ExtractionAgent(document_text)
        self.composer = ResponseComposerAgent()

    def normalize_query(self, user_query: str) -> str:
        q = user_query.lower()
        replacements = {
            "extrat": "extract", "exract": "extract", "summarise": "summarize",
            "locaton": "location", "thsi": "this", "eho": "who",
            "sighned": "signed", "shoe": "show", "amd": "and",
            "animls": "animals", "boks": "books",
            "deadlin": "deadline", "giv": "give", "summry": "summary",
            "explan": "explain",
        }
        for wrong, correct in replacements.items():
            q = q.replace(wrong, correct)
        return q

    def split_into_intent_chunks(self, query: str) -> list[str]:
        pattern = r"\b(then|also|next)\b"
        chunks = re.split(pattern, query)

        clean_chunks = []
        buffer = ""

        for part in chunks:
            part = part.strip()
            if part in ["then", "also", "next"]:
                if buffer:
                    clean_chunks.append(buffer.strip())
                buffer = ""
            else:
                buffer += " " + part

        if buffer.strip():
            clean_chunks.append(buffer.strip())

        # Also split "X and extract Y" / "X ans extract Y" into [X, extract Y]
        expanded = []
        and_extract_pattern = r"\s+an(?:d|s)\s+(?=extract|list|show|find|give\b)"
        for c in clean_chunks:
            expanded.extend(p.strip() for p in re.split(and_extract_pattern, c, flags=re.IGNORECASE) if p.strip())

        return expanded

    def classify_intent(self, user_query: str) -> list[tuple[str, str]]:
        q = self.normalize_query(user_query)
        parts = self.split_into_intent_chunks(q)

        tasks = []

        for part in parts:
            if not part:
                continue

            added = False

            summary_related = any(w in part for w in ["summarize", "summary", "key insight", "key idea", "main idea", "overall idea"])
            if summary_related:
                tasks.append(("summary", part))
                added = True

            # "list X and their Y" / "show X and their Y" = structured list, not entity extraction
            # Don't add entities when "give summary" / "give key idea" etc - summary intent covers it
            list_show = any(w in part for w in ["extract", "list", "show", "find", "give"])
            relationship = any(p in part.lower() for p in ["and their", "with their", "and its"])
            if list_show and not relationship and not summary_related:
                tasks.append(("entities", part))
                added = True
            elif list_show and relationship:
                tasks.append(("qa", part))
                added = True

            if not added:
                tasks.append(("qa", part))
        return tasks

    def handle(self, user_query: str) -> list[dict]:
        normalized_query = self.normalize_query(user_query)
        json_mode = "json" in normalized_query

        tasks = self.classify_intent(user_query)
        tasks.sort(key=lambda x: 0 if x[0] == "summary" else 1)

        flow = " -> ".join(t[0] for t in tasks)
        if json_mode:
            flow += " -> json"
        is_multi = len(tasks) > 1 or (len(tasks) == 1 and json_mode)
        print(f"[Intent] {'multi' if is_multi else 'single'} intent: {flow}")

        json_output = {}
        outputs = []

        def _try_parse_json(s: str):
            """Parse string as JSON if valid; return parsed object or original string."""
            if not s or not isinstance(s, str):
                return s
            t = s.strip().lstrip("- ").strip()
            try:
                parsed = json.loads(t)
                return parsed if isinstance(parsed, (dict, list)) else s
            except (json.JSONDecodeError, TypeError):
                return s

        for intent, query_part in tasks:

            if intent == "summary":
                summary = self.analyst.summarize(query_part)
                if json_mode:
                    json_output["summary"] = _try_parse_json(summary)
                else:
                    outputs.append(summary)

            elif intent == "entities":
                result = self.extractor.extract_entities("extract entities: " + query_part)["entities"]

                if json_mode:
                    json_output["entities"] = result
                else:
                    if not result:
                        outputs.append("No valid entities found in this document.")
                    else:
                        lines = [f"{k} = [{', '.join(v)}]" for k, v in result.items()]
                        outputs.append("\n\n".join(lines))


            elif intent == "qa":
                answer = self.analyst.answer(query_part)
                if json_mode:
                    try:
                        parsed = json.loads(answer.strip())
                        if isinstance(parsed, dict) and len(parsed) == 1:
                            k, v = next(iter(parsed.items()))
                            if k.lower() in ("summary", "answer", "text") and isinstance(v, str):
                                json_output["answer"] = v
                            else:
                                json_output["answer"] = parsed
                        elif isinstance(parsed, (dict, list)):
                            json_output["answer"] = parsed
                        else:
                            json_output["answer"] = answer
                    except (json.JSONDecodeError, TypeError):
                        json_output["answer"] = answer
                else:
                    outputs.append(answer)

        # 🔒 HARD GUARANTEE: NEVER RETURN None
        if json_mode:
            return self.composer.compose([json_output])

        return self.composer.compose(outputs or [])

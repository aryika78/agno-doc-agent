from agents.document_analyst_agent import DocumentAnalystAgent
from agents.extraction_agent import ExtractionAgent
from agents.response_composer_agent import ResponseComposerAgent
from prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from azure_client import client, DEPLOYMENT_REASONING


class OrchestratorAgent:
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.analyst = DocumentAnalystAgent(document_text)
        self.extractor = ExtractionAgent(document_text)
        self.composer = ResponseComposerAgent()

    def decide_agents(self, user_query: str) -> list[str]:
        prompt = ORCHESTRATOR_PROMPT.format(user_query=user_query)

        response = client.chat.completions.create(
            model=DEPLOYMENT_REASONING,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        decision = response.choices[0].message.content.strip().lower()
        return [a.strip() for a in decision.split(",")]

    def handle(self, user_query: str) -> str:
        outputs = []
        agents_to_call = self.decide_agents(user_query)

        for agent in agents_to_call:
            if agent == "document_analyst":
                if "summarize" in user_query.lower():
                    outputs.append(self.analyst.summarize(user_query))
                else:
                    outputs.append(self.analyst.answer(user_query))

            elif agent == "extraction_agent":
                if "json" in user_query.lower():
                    outputs.append(self.extractor.extract_json())
                else:
                    outputs.append(self.extractor.extract_entities(user_query))

        return self.composer.compose(outputs)

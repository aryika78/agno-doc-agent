from document_loader import load_document
from agents.orchestrator_agent import OrchestratorAgent


def load_new_document():
    path = input("\nEnter document path (pdf/txt/docx): ").strip().strip('"')
    return load_document(path)


print("=== Prompt-Orchestrated Multi-Agent Document System ===")

document_text = load_new_document()

while True:
    user_query = input("\nAsk something (or type 'new' to load another doc, 'exit' to quit): ").lower()

    if user_query == "exit":
        break

    if user_query == "new":
        document_text = load_new_document()
        continue

    orch = OrchestratorAgent(document_text)
    response = orch.handle(user_query)

    print("\n=== RESPONSE ===\n")
    print(response)

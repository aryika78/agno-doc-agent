from agent import route_query
from document_loader import load_document
from agents.orchestrator_agent import OrchestratorAgent


def load_new_document():
    path = input("\nEnter document path (pdf/txt/docx): ").strip().strip('"')
    return load_document(path)


print("=== Prompt-Orchestrated Document Agent ===")

document_text = load_new_document()

while True:
    user_query = input("\nAsk something (or type 'new' to load another doc, 'exit' to quit): ").lower()

    if user_query == "exit":
        break

    if user_query == "new":
        document_text = load_new_document()
        continue

    # ✅ New multi-agent flow
    orch = OrchestratorAgent(document_text)

    try:
        response = orch.handle(user_query)

        # Fallback if orchestrator gives nothing
        if not response.strip():
            raise ValueError("Empty orchestrator response")

    except Exception:
        # Old router fallback
        response = route_query(user_query, document_text)

    print("\n=== RESPONSE ===\n")
    print(response)

from agent import route_query
from document_loader import load_document

path = input("Enter document path (pdf/txt/docx): ").strip().strip('"')
document_text = load_document(path)

while True:
    user_query = input("\nAsk something about the document (or type exit): ")

    if user_query.lower() == "exit":
        break

    response = route_query(user_query, document_text)

    print("\n=== RESPONSE ===\n")
    print(response)

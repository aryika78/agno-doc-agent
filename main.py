from agent import route_query

document_text = """
John Doe signed a contract on 12th Jan 2024 with ABC Corp.
The payment amount is $5000 due before 30th Jan 2024.
"""

while True:
    user_query = input("\nAsk something about the document (or type exit): ")

    if user_query.lower() == "exit":
        break

    response = route_query(user_query, document_text)

    print("\n=== RESPONSE ===\n")
    print(response)

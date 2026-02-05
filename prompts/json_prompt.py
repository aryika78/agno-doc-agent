JSON_PROMPT = """
Extract ALL entities from the document in JSON format.

CRITICAL RULES:
1. Scan the ENTIRE document for ALL entity types
2. Include standard entities AND any unique ones you find
3. If a category has no values, use empty array []
4. Add new categories for any additional entity types found (skills, products, projects, etc.)

DOCUMENT:
{document_text}

Output valid JSON including ALL entity types found in the document.

Standard categories (always include):
- people
- organizations  
- dates
- amounts
- locations
- deadlines

Additional categories (include if found):
- books
- animals
- emails
- phone_numbers
- skills
- projects
- products
- Any other relevant entity type

Example output format:
{{
  "people": ["Mr. Rahul Mehta"],
  "organizations": ["Orion Technologies"],
  "dates": ["12 January 2024", "30 March 2024"],
  "amounts": ["5,00,000 INR"],
  "locations": ["Ahmedabad, India"],
  "deadlines": ["end of Q1 2024"],
  "books": ["Clean Code", "Atomic Habits"],
  "animals": ["Rex (German Shepherd)", "Bruno (Labrador)"]
}}

Output complete JSON:
"""
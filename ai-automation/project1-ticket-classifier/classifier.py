import anthropic
import json
import csv
import sys


client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a support ticket classifier for a SaaS company. Analyze each ticker3t and return a structured JSON
   
RULES: 
 1. Respond with only valid JSON. No other text, no markdown, no code blocks.
 2. Use EXACTLY these categories: billing, authenticaction, technical, feature_request, general
 3. Use EXACTLY these priority levels: high, medium, low
 4. Use EXACTLY these sentiment values: frsutrated, neutral, satisfied


Examples:

Input: "I can't log into my account. I've tried resetting my password three times."
Output: {"category": "feature_request", "priority": "low", "sentiment": "neutral", "summary": "Customer requesting dark mode feature for dashboard", "suggested_response": "Thank you for the suggestion! I've logged this as a feature request with our product team. We'll notify you if dark mode gets added to our roadmap."}"""

VALID_CATEGORIES = ["billing", "authentication", "technical", "feature_request", "general"]
VALID_PRIORITIES = ["high", "medium", "low"]
VALID_SENTIMENTS = ["frustrated", "neutral", "satisfied"]

def classify_ticket(subject, body): 
    ticket_text = f"subject: {subject}\nBody: {body}"
    try: 
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Classify this ticket: {ticket_text}"}
            ]
        )
        raw = message.content[0].text
        result = json.loads(raw)
        return result, message.usage
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": raw}, None
    except Exception as e:
        return {"error":str(e)}, None
    

def validate_result(result):
    errors = []
    if result.get("category") not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {result.get('category')}")
    if result.get("priority") not in VALID_PRIORITIES:
        errors.append(f"Invalid priority: {result.get('priority')}")
    if result.get("sentiment") not in VALID_SENTIMENTS:
        errors.append(f"Invalid sentiment: {result.get('sentiment')}")
    if not result.get("summary"):
        errors.append("Missing summary")
    if not result.get("suggested_response"):
        errors.append("Missing suggested_response")
    return errors

def load_tickets(filename):
    tickets = []
    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                tickets.append(row)
        return tickets
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        sys.exit(1)

def main():
   # Get input file from command line or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "sample_tickets.csv"
    
    print(f"\nInput file: {input_file}")
    tickets = load_tickets(input_file)

    # Process each ticket
    results = []
    total_input_tokens = 0
    total_output_tokens = 0

    for ticket in tickets:
        print(f"processing ticket #{ticket['id']}: {ticket['subject'][:50]}...")

        result, usage = classify_ticket(ticket['subject'], ticket['body'])


        # validate
        errors = validate_result(result)
        if errors:
            print(f" VALIDATION ERRORS: {errors}")

        # Track tokens
        if usage:
            total_input_tokens += usage.input_tokens
            total_output_tokens += usage.output_tokens

        # Add original ticcket info to result
        result["ticket_id"] = ticket["id"]
        result["customer_email"] = ticket["customer_email"]
        result["original_subject"] = ticket["subject"]
        results.append(result)

        print(f" -> {result.get('category', 'unknown')} | {result.get('priority', 'unknown')} | {result.get('sentiment', 'unknown')}")

    # Write results
    with open("classification_results.json", "w") as file:
        json.dump(results, file, indent=2)


    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tickets processed: {len(results)}")
    print(f"Total tokens used: {total_input_tokens} input, {total_output_tokens} output")
     
    # Category breakdown
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    print("\nCategory breakdown:")
    for cat, count in categories.items():
        print(f" {cat}: {count}")


    # Priority breakdown
    priorities = {}
    for r in results:
        pri = r.get("priority", "unknown")
        priorities[pri] = priorities.get(pri, 0) + 1
    print("\nPriority breakdown:")
    for pri, count in priorities.items():
        print(f" {pri}: {count}")

    print(f"\nResults saved to classification_results.json")

if __name__ == "__main__":
    main()    

          








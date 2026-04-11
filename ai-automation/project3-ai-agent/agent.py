import anthropic
import sqlite3
import json
from datetime import datetime


client = anthropic.Anthropic()
MAX_ITERATIONS = 10


tools = [
    {
        "name": "query_database",
        "description": "Execute a read-only SQL query against the business database. Tables: 'customers' (id, name, email, plan, monthly_spend, signup_date) and 'support_tickets' (id, customer_id, subject, status, created_at). Use this to look up customer information, ticket data, or run analytics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type":  "string",
                    "description": "A SELECT SQL query to execute"

                }
            },
            "required": ["sql"]
        }
    },
    {
        "name": "calculator",
        "description": "performs math calculations. Use for percentages, averages, or any arithmentic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate, e.g. '25 * 4 + 10'"
                }
            },
            "required": ["expression"]
        }
    }
]


SYSTEM_PROMPT = """You are a business analytics agent with access to a customer database. Use the available tools to answer questions accurately. When asked follow-up questions, use context from the conversation to understand what the user is referring to, Always base your answer on actual data from the database, not assumptions."""


def run_tool(name, inputs):
    if name == "query_database":
        sql = inputs["sql"].strip().upper()
        if not sql.startswith("SELECT"):
            return json.dumps({"error": "Only SELECT queries are allowed"})
        try:
            db = sqlite3.connect("business.db")
            cursor = db.cursor()
            cursor.execute(inputs["sql"])
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            db.close()
            return json.dumps({"columns": columns, "rows": rows})
        except Exception as e:
            return json.dumps({"error": str(e)})
    elif name == "calculator":
        try:
            expression = inputs["expression"]
            allowed = set("0123456789+-*/().% ")
            if not all(c in allowed for c in expression):
                return "Error: invalid characters in expression"
            return str(eval(expression))
        except Exception as e: 
            return f"Error: {e}"
    return json.dumps({"error": f"Unknown tool: {name}"})


def ask_agent(question, conversation_history):
    #Build messages with conversation history
    messages = list(conversation_history)
    messages.append({"role": "user", "content": question})

    log = []

    for iteration in range(MAX_ITERATIONS):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            system=SYSTEM_PROMPT,
            messages=messages
        )


        tool_used = False
        tool_results = []
        text_blocks = []


        for block in response.content:
            if block.type == "tool_use":
                tool_used = True
                print(f"    [Step {iteration + 1}: {block.name}({json.dumps(block.input)[:100]})]")
                result = run_tool(block.name, block.input)
                print(f"    [Result: {result[:150]}]")
                log.append({
                    "type": "tool_call",
                    "step": iteration + 1,
                    "tool": block.name,
                    "input": block.input,
                    "result": result[:500]
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id, 
                    "content": result
                })

            elif block.type == "text" and block.text:
                text_blocks.append(block.text)

        if not tool_used:
            for text in text_blocks:
                print(f"\nAssistant: {text}")
                log.append({"type": "answer", "text": text})
            break

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"    [WARNING: Hit max iterations ({MAX_ITERATIONS})]")

    # Return the final answer text and updated messages for history
    answer_text = " ".join(text_blocks) if text_blocks else "No answer generated"
    messages.append({"role": "assistant", "content": response.content})
    return answer_text, messages, log

def main():
    print("=" * 50)
    print("BUSINESS ANALYTICS AGENT")
    print("Type 'quit' to exit, 'clear' to reset history")
    print("=" * 50 + "\n")


    conversation_history = []
    all_logs =[]


    while True:
        question = input("You: ")
        if question.lower() in ["quit", "exit", "q"]:
            print ("Goodbye!")
            break
        if question.lower() == "clear":
            conversation_history = []
            print("Conversation history cleared.\n")
            continue
        if not question.strip():
            continue

        answer, conversation_history, log = ask_agent(question, conversation_history)
        all_logs.append({"question": question, "log": log})
        print()

    # Save logs on exit
    with open("agent_log.json", "w") as f:
        json.dump({
            "timestamp": str(datetime.now()),
            "queries": all_logs
        }, f, indent=2)
    print("Logs saved to agent_log.json")

if __name__ == "__main__":
    main()

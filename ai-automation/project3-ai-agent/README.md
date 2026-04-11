cat > README.md << 'READMEEOF'
# Multi-Tool AI Agent

An AI-powered business analytics agent that uses Claude to answer questions about customer data. The agent has access to a SQL database and a calculator, and chains multiple tools together to answer complex analytical questions.

## How It Works

User asks a question
|
[Claude reasons about which tool(s) to use]
|
[Tool execution: database query / calculator]
|
[Results sent back to Claude]
|
[Claude either uses another tool or gives final answer]
|
Response with data-backed insights


## Key Features

- **Multi-tool chaining** — Agent automatically chains database queries and calculations to answer complex questions
- **SQL generation** — Claude writes its own SQL queries based on natural language questions
- **Conversation memory** — Handles follow-up questions like "do they have any tickets?" by understanding context
- **Safety controls** — Only SELECT queries allowed, calculator input validation, max iteration limit
- **Agent logging** — Every tool call and result saved to JSON for debugging and auditing
- **Error recovery** — Agent adapts when a tool fails, finding alternative approaches
- **CLI support** — Use interactively or pass a single question as argument

## Architecture

The agent uses a **reasoning loop**:

1. Claude receives the question and list of available tools
2. Claude decides which tool to use and with what inputs
3. Application executes the tool and returns the result
4. Claude reads the result and either:
   - Requests another tool (loop continues)
   - Gives a final answer (loop ends)

The LLM reasons and decides. The application executes. This separation keeps the agent safe and controllable.

## Tools

| Tool | Description | Safety |
|------|-------------|--------|
| query_database | Executes SQL against SQLite database | SELECT only, parameterized |
| calculator | Evaluates math expressions | Character whitelist validation |

## Database Schema

**customers**: id, name, email, plan, monthly_spend, signup_date
**support_tickets**: id, customer_id, subject, status, created_at

## Tech Stack

- **Python 3** — Core application
- **Anthropic SDK** — Claude API with tool use
- **SQLite** — Local database for business data
- **JSON logging** — Full audit trail of agent decisions

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/sre-devops-ai-projects.git
cd sre-devops-ai-projects/ai-automation/project3-ai-agent

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Create the sample database
python3 setup_db.py
```

## Usage

### Interactive Mode
```bash
python3 agent.py
```

### Single Question Mode
```bash
python3 agent.py "How many customers do we have on each plan?"
```

### Example Conversation

You: Who is our highest paying customer?
Agent: Sarah Chen from TechCorp, $499.99/month on enterprise plan.
You: Do they have any open tickets?
Agent: Yes, 1 open ticket: "API rate limit hitting too often" (March 1, 2026)
You: What percentage of revenue comes from enterprise customers?
Agent: [queries database] [calculates] Enterprise generates 86.21% of total revenue.

## Prompt Engineering Approach

- **System prompt** defines the agent's role as a business analytics assistant
- **Tool descriptions** are detailed enough for Claude to choose the right tool
- **Input schemas** define required parameters with clear descriptions
- **Max iterations (10)** prevents infinite tool-calling loops
- **SQL safety** — only SELECT queries pass validation
- **Calculator safety** — character whitelist blocks code injection
READMEEOF
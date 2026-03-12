# AI Support Ticket Classifier

A Python CLI tool that uses Claude AI to automatically classify customer support tickets. It analyzes tickets from a CSV file and returns structured classifications including category, priority, sentiment, and suggested responses.

## What It Does

- Reads support tickets from a CSV file
- Sends each ticket to Claude (Anthropic API) for analysis
- Returns structured JSON with: category, priority, sentiment, summary, and suggested response
- Validates all AI outputs against expected values
- Tracks token usage for cost monitoring
- Generates summary statistics (category and priority breakdowns)

## Architecture
```
CSV Input → Load Tickets → Claude API Classification → Validate Output → JSON Results
                                    |
                          System Prompt with:
                          - Explicit category rules
                          - Few-shot examples
                          - JSON output format
                          - Temperature=0 for consistency
```

## Tech Stack

- **Python 3** — Core scripting
- **Anthropic SDK** — Claude API integration
- **Prompt Engineering** — Few-shot examples, structured JSON output, temperature control
- **Output Validation** — Verifies AI responses against expected values

## Setup
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-automation-projects.git
cd ai-automation-projects/project1-ticket-classifier

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage
```bash
# Use default sample data
python3 classifier.py

# Use your own CSV file
python3 classifier.py your_tickets.csv
```

### CSV Format

Your input CSV must have these columns:

| Column | Description |
|--------|-------------|
| id | Ticket ID |
| subject | Ticket subject line |
| body | Full ticket body text |
| customer_email | Customer email address |

### Output

Results are saved to `classification_results.json` with this structure:
```json
{
  "ticket_id": "1",
  "category": "billing",
  "priority": "high",
  "sentiment": "frustrated",
  "summary": "Customer charged twice for subscription",
  "suggested_response": "I apologize for the duplicate charge...",
  "customer_email": "sarah@example.com",
  "original_subject": "Charged twice for subscription"
}
```

## Prompt Engineering Approach

1. **Explicit constraints** — Valid categories, priorities, and sentiments are locked down in the system prompt
2. **Few-shot examples** — Input/output pairs teach Claude the exact format
3. **Temperature=0** — Deterministic output for consistent classification
4. **Output validation** — Every response is verified before being accepted

## Cost

Processing 8 tickets: ~2,100 input tokens, ~850 output tokens (less than $0.01)

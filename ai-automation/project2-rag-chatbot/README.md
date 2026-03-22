# RAG Knowledge Base Chatbot

An AI-powered chatbot that answers questions from your company documentation using Retrieval Augmented Generation (RAG). Built with Python, ChromaDB, and the Claude API.

## How It Works
```
User asks a question
       |
[Query Rewriting] — Resolves follow-up context using conversation history
       |
[Vector Search] — Finds semantically similar document chunks in ChromaDB
       |
[Distance Check] — Rejects queries with no relevant documents (prevents hallucination)
       |
[Answer Generation] — Claude generates an answer using ONLY the retrieved context
       |
Response with source citations
```

## Key Features

- **Semantic search** — Finds relevant documents even when exact keywords don't match
- **Paragraph-based chunking** — Documents split into meaningful units for precise retrieval
- **Query rewriting** — Handles follow-up questions by resolving pronouns and context
- **Hallucination protection** — Two layers: distance threshold filtering + system prompt constraints
- **Source citations** — Every answer references which document it came from
- **Multi-turn conversations** — Maintains conversation history for contextual follow-ups
- **CLI support** — Use interactively or pass a single question as argument

## Tech Stack

- **Python 3** — Core application
- **Anthropic SDK** — Claude API for answer generation and query rewriting
- **ChromaDB** — Local vector database for semantic search
- **Embeddings** — all-MiniLM-L6-v2 model (auto-downloaded by ChromaDB)

## Setup
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/sre-devops-ai-projects.git
cd sre-devops-ai-projects/ai-automation/project2-rag-chatbot

# Create virtual environment (use Python 3.13)
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

### Interactive Mode
```bash
python3 chatbot.py
```

### Single Question Mode
```bash
python3 chatbot.py "How do I get a refund?"
```

### Adding Your Own Documents
Place markdown files in the `docs/` directory. The chatbot automatically loads and chunks all `.md` files on startup.

## Architecture Decisions

- **Paragraph chunking over word chunking** — Preserves semantic units, gives more focused retrieval results
- **Query rewriting** — Uses Claude to convert follow-up questions into standalone queries before vector search
- **Distance threshold (1.5)** — Queries with no close document match are rejected without calling Claude, saving API costs and preventing hallucination
- **Temperature 0** — Deterministic responses for consistent, factual answers

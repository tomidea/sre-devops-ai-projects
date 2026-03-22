import chromadb
import anthropic
import os
import json
import sys

# Configuration
DOCS_DIR = "docs"
COLLECTION_NAME = "Knowledge_base"
MAX_RESULTS = 3
DISTANCE_THRESHOLD = 1.5

ai = anthropic.Anthropic()
db = chromadb.Client()

SYSTEM_PROMPT = """You are a helpful support assistant. Answer questions using ONLY the provided context. If the context does not contain the answer, say "I don't have that information in my knowledge base." Be concise. Cite which document your answer came from."""


def load_and_store_docs():
    collection = db.create_collection(COLLECTION_NAME)
    chunk_count = 0

    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".md"):
            continue
        with open(os.path.join(DOCS_DIR, filename), "r") as f:
            content = f.read()


        # Paragraph-based chunking, skip short chunks
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and len(p.split()) > 5]

        for i, para in enumerate(paragraphs):
            collection.add(
                documents=[para],
                ids=[f"{filename}_p{i}"],
                metadatas=[{"source": filename}]
            )
            chunk_count += 1


    print(f"Loaded {chunk_count} chunks from {DOCS_DIR}/")
    return collection

def rewrite_query(question, history):
    if not history:
        return question
    rewrite = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        temperature=0,
        system="Rewrite the user's question as a standalone question using conversation history. Return ONLY the rewritten question, nothing else.",
        messages=[
            {"role": "user", "content": f"History:\n{history[-4:]}\n\nLatest question: {question}"}

        ]
    )
    return rewrite.content[0].text

def retrieve(collection, query):
    results = collection.query(query_texts=[query], n_results=MAX_RESULTS)
    top_distance = results['distances'][0][0]
    documents = results['documents'][0]
    sources = list(set(r['source'] for r in results['metadatas'][0]))
    return documents, sources, top_distance

def generate_answer(question, context, history):
    messages = []
    for role, content in history:
        messages.append({"role": role, "content": content})
    messages.append({
        "role": "user",
        "content": f"Context from knowledge base:\n{context}\n\nQuestion: {question}"
    })
    response = ai.messages.create(
        model="claude-4-sonnet-20250514",
        max_tokens=512,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text

def ask(collection, question, history):
    # Step 1: Rewrite query for better retrieval
    search_query = rewrite_query(question, history)

    # Step 2: Check distance threshold
    documents, sources, distance = retrieve(collection, search_query)

    # Step 3: Check distance threshold
    if distance > DISTANCE_THRESHOLD:
        return "I dont have information about that in my knowledge base.", [], distance

    # Step 4: Generate answer with context
    context = "\n\n---\n\n".join(documents)
    answer = generate_answer(question, context, history)
    return answer, sources, distance
      

def main():
    print("=" * 50)
    print("RAG KNOWLEDGE BASE CHATBOT")
    print("=" * 50)

    # Load documents
    collection = load_and_store_docs()

    # Check if user passed a single question as argument
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        answer, sources, distance = ask(collection, question, [])
        print(f"\nQ: {question}")
        print(f"A: {answer}")
        if sources:
            print(f"Sources: {', '.join(sources)}")
        return
    
    #Interactive chat loop
    print("Type 'quit' to exit\n")
    history = []

    while True:
        question = input("You: ")
        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if not question.strip():
            continue

        answer, sources, distance = ask(collection, question, history)
        print(f"\nAssistant: {answer}")
        if sources:
            print(f"(Sources: {', '.join(sources)} | Distance: {distance:.4f})")
        print()


        # Save to history
        history.append(("user", question))
        history.append(("assistant", answer))


if __name__ == "__main__":
    main()
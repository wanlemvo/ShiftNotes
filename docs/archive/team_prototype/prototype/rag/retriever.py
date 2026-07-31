"""
retriever.py
ShiftNotes RAG — Retrieval and Generation

Handles semantic search against the ChromaDB index
and answer generation via the Claude API.
"""

import json
import time
import pathlib
import datetime
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer

RAG_DIR     = pathlib.Path(__file__).parent
CHROMA_PATH = RAG_DIR / "chroma_db"
LOG_FILE    = RAG_DIR / "query_log.jsonl"
EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION  = "shift_reports"
GROQ_MODEL  = "llama-3.3-70b-versatile"


def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL)


def get_collection(chroma_path: pathlib.Path = CHROMA_PATH) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(chroma_path))
    return client.get_collection(COLLECTION)


def retrieve(
    question: str,
    kiosk: str = None,
    week: int = None,
    n_results: int = 5,
    model: SentenceTransformer = None,
    collection: chromadb.Collection = None,
) -> list[dict]:
    """
    Retrieve the top-N most relevant reports for a question.
    Optionally filter by kiosk and/or week before semantic search.
    """
    if model is None:
        model = get_embedding_model()
    if collection is None:
        collection = get_collection()

    where = {}
    if kiosk and kiosk != "All":
        where["kiosk"] = kiosk
    if week and week != 0:
        where["week"] = week

    query_embedding = model.encode([question])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        where=where if where else None,
        include=["documents", "metadatas"],
    )

    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({"text": doc, "meta": meta})
    return hits


def generate_answer(question: str, hits: list[dict], api_key: str = None) -> str:
    """
    Generate a grounded answer using Claude with the retrieved reports as context.
    """
    context_parts = []
    for h in hits:
        m = h["meta"]
        context_parts.append(
            f"[Report {m['report_id']} | {m['kiosk']} | {m['date']} | Lead: {m['lead_name']}]\n{h['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an operational intelligence assistant for ShiftNotes. "
                    "Answer questions using only the shift report excerpts provided. "
                    "Be concise and specific. Reference kiosks, dates, and employees by name when relevant. "
                    "If the context does not contain enough information to answer, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nShift Report Context:\n{context}",
            },
        ],
    )

    return response.choices[0].message.content


def generate_answer_mcp(question: str, hits: list[dict], api_key: str = None) -> str:
    """
    MCP-style tool wrapper for answer generation.
    Separates tool definition from tool execution.
    """
    tool_input = {
        "name": "generate_operational_answer",
        "description": "Generate a grounded answer from shift report context",
        "input": {
            "question": question,
            "context_reports": [
                {
                    "report_id": h["meta"]["report_id"],
                    "kiosk": h["meta"]["kiosk"],
                    "date": h["meta"]["date"],
                    "text": h["text"],
                }
                for h in hits
            ],
        },
    }
    # Execute the tool
    return generate_answer(question, hits, api_key=api_key)


def query(
    question: str,
    kiosk: str = None,
    week: int = None,
    n_results: int = 5,
    api_key: str = None,
    model: SentenceTransformer = None,
    collection: chromadb.Collection = None,
) -> tuple[str, list[dict]]:
    """
    Full RAG pipeline: retrieve relevant reports then generate an answer.
    Returns (answer, hits) so callers can display source reports if needed.
    """
    t_start = time.time()
    hits = retrieve(question, kiosk=kiosk, week=week, n_results=n_results,
                    model=model, collection=collection)
    answer = generate_answer_mcp(question, hits, api_key=api_key)
    latency = time.time() - t_start

    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "question": question,
        "kiosk_filter": kiosk or "All",
        "week_filter": week or "All",
        "hits_returned": len(hits),
        "report_ids": [h["meta"]["report_id"] for h in hits],
        "response_length": len(answer),
        "latency_seconds": round(latency, 3),
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return answer, hits

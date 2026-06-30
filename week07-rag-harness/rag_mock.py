"""
Simple RAG mock — retrieve context then build a templated answer.

Complex RAG (multi-step) comes in later weeks; this is Simple RAG.
"""

from retriever import load_corpus, retrieve


def simple_rag_answer(query: str, corpus=None) -> dict:
    if corpus is None:
        corpus = load_corpus()
    hits = retrieve(query, corpus, top_k=1)
    if not hits or hits[0]["score"] == 0:
        return {
            "query": query,
            "answer": "I could not find relevant policy information.",
            "citations": [],
            "retrieved_chunks": hits,
        }

    top = hits[0]
    answer = (
        f"Based on {top['doc_id']}: {top['text']}"
    )
    return {
        "query": query,
        "answer": answer,
        "citations": [{"doc_id": top["doc_id"], "chunk_id": top["chunk_id"]}],
        "retrieved_chunks": hits,
    }

"""
Week 3 — Citation correctness and answer grounding checks.

Citation: does the cited doc_id/chunk_id exist and match what was retrieved?
Grounding: do factual claims in the answer (amounts) appear in the source chunk?
"""

import re

_AMOUNT_RE = re.compile(r"\$\s*[0-9,]+\.\d{2}")


def normalize_amount(amount: str) -> str:
    match = _AMOUNT_RE.search(amount)
    if not match:
        return amount.strip()
    return match.group(0).replace(" ", "")


def extract_amounts(text: str) -> list[str]:
    return [normalize_amount(m.group(0)) for m in _AMOUNT_RE.finditer(text)]


def citation_exists(citation: dict, corpus: list[dict]) -> bool:
    doc_id = citation.get("doc_id")
    chunk_id = citation.get("chunk_id")
    return any(c["doc_id"] == doc_id and c["chunk_id"] == chunk_id for c in corpus)


def citation_matches_retrieval(citation: dict, retrieved_chunk_ids: list[str]) -> bool:
    if not citation or not retrieved_chunk_ids:
        return False
    return citation.get("chunk_id") in retrieved_chunk_ids


def validate_citations(
    citations: list[dict],
    retrieved_chunks: list[dict],
    corpus: list[dict],
) -> dict:
    """
    Returns:
        citation_present, citation_valid, citation_matches_retrieval, pass
    """
    if not citations:
        return {
            "citation_present": False,
            "citation_valid": False,
            "citation_matches_retrieval": False,
            "pass": False,
        }

    primary = citations[0]
    retrieved_ids = [c["chunk_id"] for c in retrieved_chunks]
    valid = citation_exists(primary, corpus)
    matches = citation_matches_retrieval(primary, retrieved_ids)

    return {
        "citation_present": True,
        "citation_valid": valid,
        "citation_matches_retrieval": matches,
        "pass": valid and matches,
    }


def validate_grounding(answer: str, source_text: str) -> dict:
    """
    Grounding rule (demo): every dollar amount in the answer must appear in source_text.
    Unstated amounts in the answer = potential hallucination.
    """
    answer_amounts = extract_amounts(answer)
    if not answer_amounts:
        return {
            "amounts_in_answer": [],
            "ungrounded_amounts": [],
            "pass": True,
        }

    source_amounts = {normalize_amount(a) for a in extract_amounts(source_text)}
    ungrounded = [a for a in answer_amounts if a not in source_amounts]

    return {
        "amounts_in_answer": answer_amounts,
        "ungrounded_amounts": ungrounded,
        "pass": len(ungrounded) == 0,
    }


def validate_rag_response(
    answer: str,
    citations: list[dict],
    retrieved_chunks: list[dict],
    corpus: list[dict],
) -> dict:
    cite = validate_citations(citations, retrieved_chunks, corpus)
    source_text = retrieved_chunks[0]["text"] if retrieved_chunks else ""
    ground = validate_grounding(answer, source_text)

    return {
        "citation": cite,
        "grounding": ground,
        "pass": cite["pass"] and ground["pass"],
    }

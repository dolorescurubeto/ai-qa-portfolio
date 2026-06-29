"""
Week 5 — Explore BERT attention matrices and relevant tokens.

Extends the course exercise AutoAtencion.py with readable token analysis
and an optional attention heatmap.

Usage:
  cd week05-attention
  python attention_explorer.py
  python attention_explorer.py --spanish
  python attention_explorer.py --heatmap
"""

import argparse
import string
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from transformers import BertModel, BertTokenizer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"

BANKING_SENTENCE = "Your checking account balance is $1,847.32."
SPANISH_SENTENCE = "Un gato está sentado a la sombra abajo de un árbol"

STRUCTURAL_TOKENS = {"[CLS]", "[SEP]"}


def load_model():
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased", output_attentions=True)
    model.eval()
    return tokenizer, model


def get_attention(tokens: dict, model) -> tuple[list[int], torch.Tensor]:
    with torch.no_grad():
        outputs = model(**tokens)

    attn = outputs.attentions[-1][0].mean(dim=0)
    input_ids = tokens["input_ids"][0].tolist()
    return input_ids, attn


def token_labels_from_ids(tokenizer, input_ids: list[int]) -> list[str]:
    return tokenizer.convert_ids_to_tokens(input_ids)


def is_content_token(label: str) -> bool:
    """Skip special tokens, punctuation, and number fragments."""
    if label in STRUCTURAL_TOKENS:
        return False
    if label in {".", ",", "$"}:
        return False
    if label.isdigit():
        return False
    if len(label) == 1 and label in string.punctuation:
        return False
    return True


def content_indices(token_labels: list[str]) -> list[int]:
    return [i for i, label in enumerate(token_labels) if is_content_token(label)]


def print_header(sentence: str) -> None:
    print("WEEK 5 — BERT attention explorer")
    print("=" * 60)
    print(f"Sentence: {sentence}")
    print("Model: bert-base-uncased (last layer, averaged heads)")
    print()


def print_tokens(token_labels: list[str]) -> None:
    print("Tokens:")
    for i, label in enumerate(token_labels):
        kind = "content" if is_content_token(label) else "structural/noise"
        print(f"  [{i:2d}] {label:12s}  ({kind})")
    print()
    print("Note: BERT splits amounts like $1,847.32 into many small tokens.")
    print("      Focus on content words (checking, account, balance).")
    print()


def top_targets_for_source(
    source_idx: int,
    token_labels: list[str],
    attn: torch.Tensor,
    top_k: int,
    content_only: bool,
) -> list[tuple[str, float]]:
    weights = attn[source_idx].clone()
    weights[source_idx] = 0.0

    if content_only:
        for j, label in enumerate(token_labels):
            if not is_content_token(label):
                weights[j] = 0.0

    valid_count = (weights > 0).sum().item()
    if valid_count == 0:
        return []

    k = min(top_k, int(valid_count))
    _, top_indices = torch.topk(weights, k=k)
    return [(token_labels[j], weights[j].item()) for j in top_indices.tolist()]


def print_semantic_pairs_per_token(
    token_labels: list[str], attn: torch.Tensor, top_k: int = 3
) -> None:
    print(f"Semantic attention — top {top_k} content words per token:")
    print("(ignores [CLS], [SEP], punctuation, and number fragments)")
    print("-" * 60)

    for i, source in enumerate(token_labels):
        if not is_content_token(source):
            continue

        pairs = top_targets_for_source(i, token_labels, attn, top_k, content_only=True)
        if not pairs:
            continue

        formatted = ", ".join(f"{target} ({score:.3f})" for target, score in pairs)
        print(f"  {source:15s} -> {formatted}")
    print()


def print_strongest_semantic_pairs(
    token_labels: list[str], attn: torch.Tensor, top_n: int = 8
) -> None:
    print(f"Strongest semantic pairs (top {top_n}, content words only):")
    print("-" * 60)

    pairs = []
    for i, source in enumerate(token_labels):
        if not is_content_token(source):
            continue
        for j, target in enumerate(token_labels):
            if i == j or not is_content_token(target):
                continue
            pairs.append((attn[i, j].item(), source, target, i, j))

    pairs.sort(reverse=True)
    if not pairs:
        print("  (no content pairs found)")
        print()
        return

    for score, source, target, i, j in pairs[:top_n]:
        print(f"  {source:15s} -> {target:15s}  score={score:.3f}  ({i}->{j})")
    print()


def print_banking_insights(token_labels: list[str], attn: torch.Tensor) -> None:
    """Highlight pairs relevant to the banking use case."""
    keywords = ("checking", "account", "balance", "savings", "transfer")
    print("Banking-relevant links (if present in sentence):")
    print("-" * 60)

    found = False
    for i, source in enumerate(token_labels):
        if not any(k in source.lower() for k in keywords):
            continue
        pairs = top_targets_for_source(i, token_labels, attn, top_k=3, content_only=True)
        if pairs:
            found = True
            formatted = ", ".join(f"{t} ({s:.3f})" for t, s in pairs)
            print(f"  {source:15s} -> {formatted}")

    if not found:
        print("  (no banking keywords in this sentence)")
    print()


def save_heatmap(
    token_labels: list[str],
    attn: torch.Tensor,
    output_path: Path,
    title_suffix: str = "",
    indices: list[int] | None = None,
) -> None:
    if indices is None:
        indices = list(range(len(token_labels)))

    labels = [token_labels[i] for i in indices]
    data = attn[indices][:, indices].cpu().numpy()
    size = len(labels)

    fig_w = max(8, size * 0.55)
    fig_h = max(6, size * 0.45)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    im = ax.imshow(data, cmap="Blues", vmin=0, vmax=data.max() if data.max() > 0 else 1)
    ax.set_xticks(range(size))
    ax.set_yticks(range(size))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Attended token (key)")
    ax.set_ylabel("Source token (query)")
    ax.set_title(f"BERT attention — last layer{title_suffix}")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def run(sentence: str, heatmap: bool) -> None:
    tokenizer, model = load_model()
    encoded = tokenizer(sentence, return_tensors="pt")
    input_ids, attn = get_attention(encoded, model)
    token_labels = token_labels_from_ids(tokenizer, input_ids)

    print_header(sentence)
    print_tokens(token_labels)
    print_semantic_pairs_per_token(token_labels, attn)
    print_strongest_semantic_pairs(token_labels, attn)
    print_banking_insights(token_labels, attn)

    print("Key ideas:")
    print("  - High scores between checking / account / balance = model links those concepts.")
    print("  - Attention shows focus, not correctness — use Weeks 1-4 for factual QA.")
    print("  - [SEP] and '.' often dominate raw rankings; semantic filter hides that noise.")
    print()

    if heatmap:
        full_path = REPORTS_DIR / "week05_attention_heatmap_full.png"
        save_heatmap(token_labels, attn, full_path, title_suffix=" (all tokens)")

        content_idx = content_indices(token_labels)
        semantic_path = REPORTS_DIR / "week05_attention_heatmap.png"
        save_heatmap(
            token_labels,
            attn,
            semantic_path,
            title_suffix=" (content words only)",
            indices=content_idx,
        )
        print(f"Heatmaps saved:")
        print(f"  Full:     {full_path}")
        print(f"  Semantic: {semantic_path}")


def main():
    parser = argparse.ArgumentParser(description="Explore BERT attention matrices")
    parser.add_argument(
        "--spanish",
        action="store_true",
        help="Use the course Spanish sentence instead of the banking example",
    )
    parser.add_argument(
        "--heatmap",
        action="store_true",
        help="Save attention heatmaps to reports/",
    )
    args = parser.parse_args()

    sentence = SPANISH_SENTENCE if args.spanish else BANKING_SENTENCE
    run(sentence, heatmap=args.heatmap)


if __name__ == "__main__":
    main()

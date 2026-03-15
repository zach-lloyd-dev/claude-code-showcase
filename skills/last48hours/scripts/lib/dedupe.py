"""Deduplication + cross-source linking for last48hours."""

import re
from typing import List, Set

from . import schema

STOPWORDS = frozenset({
    "the", "a", "an", "to", "for", "how", "is", "in", "of", "on",
    "and", "with", "from", "by", "at", "this", "that", "it", "my",
    "your", "i", "me", "we", "you", "what", "are", "do", "can",
    "its", "be", "or", "not", "no", "so", "if", "but", "about",
    "all", "just", "get", "has", "have", "was", "will",
})


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def get_ngrams(text: str, n: int = 3) -> Set[str]:
    text = normalize_text(text)
    if len(text) < n:
        return {text}
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def tokenize(text: str) -> Set[str]:
    words = re.sub(r"[^\w\s]", " ", text.lower()).split()
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def jaccard(set1: Set[str], set2: Set[str]) -> float:
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def hybrid_similarity(text_a: str, text_b: str) -> float:
    trigram_sim = jaccard(get_ngrams(text_a), get_ngrams(text_b))
    token_sim = jaccard(tokenize(text_a), tokenize(text_b))
    return max(trigram_sim, token_sim)


def get_item_text(item: schema.BaseItem) -> str:
    return (item.title or item.text[:100]).strip()


def dedupe_items(items: List[schema.BaseItem], threshold: float = 0.7) -> List[schema.BaseItem]:
    """Remove near-duplicates within same source, keeping highest-scored."""
    if len(items) <= 1:
        return items

    ngrams = [get_ngrams(get_item_text(item)) for item in items]
    to_remove = set()

    for i in range(len(items)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(items)):
            if j in to_remove:
                continue
            # Only dedup within same source
            if items[i].source != items[j].source:
                continue
            sim = jaccard(ngrams[i], ngrams[j])
            if sim >= threshold:
                # Remove lower-scored one
                if items[i].score >= items[j].score:
                    to_remove.add(j)
                else:
                    to_remove.add(i)

    return [item for idx, item in enumerate(items) if idx not in to_remove]


def cross_source_link(items: List[schema.BaseItem], threshold: float = 0.40) -> None:
    """Annotate items with cross-source references. Modifies in-place."""
    if len(items) <= 1:
        return

    texts = [get_item_text(item)[:100] for item in items]

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i].source == items[j].source:
                continue
            sim = hybrid_similarity(texts[i], texts[j])
            if sim >= threshold:
                if items[j].id not in items[i].cross_refs:
                    items[i].cross_refs.append(items[j].id)
                if items[i].id not in items[j].cross_refs:
                    items[j].cross_refs.append(items[i].id)

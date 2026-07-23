# ─────────────────────────────────────────────────────────────────────────────
# modules/semantic_analyser.py  –  Sentence-BERT semantic similarity
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
from typing import Dict, List, Tuple

import numpy as np

from config import SBERT_MODEL

# Lazy-load sentence-transformers
_sbert_model = None


def _get_sbert():
    global _sbert_model
    if _sbert_model is None:
        from sentence_transformers import SentenceTransformer
        _sbert_model = SentenceTransformer(SBERT_MODEL)
    return _sbert_model


# ── Utility ───────────────────────────────────────────────────────────────────

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two 1-D vectors."""
    a = a.flatten()
    b = b.flatten()
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _sentence_split(text: str) -> List[str]:
    """Naive sentence splitter (avoids NLTK dependency at import time)."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if len(s.split()) >= 3]


# ── Public API ────────────────────────────────────────────────────────────────

def compute_similarity(transcript: str, reference: str) -> float:
    """
    Compute overall semantic similarity between the transcript and the
    reference concept description.

    Returns a float in [0, 1].
    """
    if not transcript.strip() or not reference.strip():
        return 0.0

    model = _get_sbert()
    embs = model.encode([transcript, reference], convert_to_numpy=True)
    return max(0.0, min(1.0, _cosine_similarity(embs[0], embs[1])))


def identify_key_concepts(reference: str) -> List[str]:
    """
    Extract important noun phrases / keywords from the reference text.
    Simple heuristic: words longer than 4 chars, lowercased, deduped.
    """
    words = re.findall(r"\b[a-zA-Z]{5,}\b", reference)
    # Remove generic stop-words
    stopwords = {
        "which", "these", "their", "there", "about", "where", "often",
        "using", "other", "being", "include", "between", "through",
        "common", "types", "called", "known", "refers", "enables",
        "allows", "provides", "within", "across", "system", "systems",
        "based", "making", "given", "would", "could", "while"
    }
    seen: set = set()
    result: List[str] = []
    for w in words:
        lw = w.lower()
        if lw not in stopwords and lw not in seen:
            seen.add(lw)
            result.append(lw)
    return result[:20]   # top-20 keywords


def identify_gaps(transcript: str, reference: str) -> Dict[str, bool]:
    """
    Check which key concepts from the reference appear in the transcript.

    Returns a dict  {concept_keyword: covered_bool}.
    """
    keywords = identify_key_concepts(reference)
    transcript_lower = transcript.lower()
    return {kw: (kw in transcript_lower) for kw in keywords}


def sentence_level_similarity(transcript: str, reference: str) -> List[Tuple[str, float]]:
    """
    For each sentence in the transcript compute its similarity to the full
    reference.  Returns list of (sentence, score) tuples.
    """
    sentences = _sentence_split(transcript)
    if not sentences:
        return []

    model = _get_sbert()
    ref_emb  = model.encode([reference], convert_to_numpy=True)[0]
    sent_embs = model.encode(sentences,  convert_to_numpy=True)

    return [
        (s, max(0.0, min(1.0, _cosine_similarity(e, ref_emb))))
        for s, e in zip(sentences, sent_embs)
    ]

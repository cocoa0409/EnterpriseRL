"""Knowledge base with the fixed retrieval implementation (the "bm25_grep" mode).

This layer is part of the frozen scaffold: generated scenarios only supply
``{id, title, content}`` documents; indexing, search, and result formatting are
fixed here so every scenario behaves identically.

Behavior (deliberately exact):
  - Indexing: whole documents, no chunking. The BM25 index is built over the
    **content** field only, tokenized by the hybrid CJK/ASCII analyzer
    ``_tokenize`` (see below), applied identically at index and query time.

Tokenization (``_tokenize``): lowercase, then walk the text emitting
  - one token per maximal ``[a-z0-9_]`` run (English words, the discoverable
    tool ids like ``accept_package_close_99504fe8``, numbers) — same units the
    old ``.split()`` produced for ASCII; and
  - overlapping CHARACTER BIGRAMS over each maximal run of CJK ideographs
    (``占位费`` -> ``占位``, ``位费``; a length-1 run -> the single char).
  All other characters (punctuation, whitespace, markdown) are separators.
  The old ``text.lower().split()`` split only on whitespace, so a Chinese
  sentence with no internal spaces became ONE run-on token that no query term
  could ever byte-match — every CJK query scored 0 and the top-k collapsed to
  the first k docs in insertion order. CJK bigrams (the Lucene ``cjk`` analyzer
  strategy) give Chinese queries matchable units while keeping ASCII exact
  matches intact; it is pure-rule and dependency-free, so retrieval stays
  deterministic and reproducible for the frozen scaffold.
  - KB_search: BM25Okapi scoring (k1=1.5, b=0.75, epsilon=0.25 idf-floor — the
    standard Okapi formula), returns the top 10 documents by score (no score
    threshold), each formatted with rank / title / ID / score / FULL content.
  - grep: regex over each document's content, case-insensitive; an invalid
    regex falls back to a literal (escaped) match; score = number of matches;
    top 10, same full-content formatting.

Full content is returned on purpose: the business rules and the discoverable
tool names live inside the documents, so the agent must be able to read the
whole policy from one search result.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Maximal run of ASCII word chars = one token (English words, tool ids, numbers).
_ASCII_RUN = re.compile(r"[a-z0-9_]+")


def _is_cjk(ch: str) -> bool:
    """CJK Unified Ideographs (basic block) — the Chinese characters in the corpus."""
    return "一" <= ch <= "鿿"


def _tokenize(text: str) -> List[str]:
    """Hybrid analyzer (see module docstring): ASCII runs kept whole, CJK runs
    emitted as overlapping character bigrams; everything else is a separator.
    Used identically at index and query time."""
    text = text.lower()
    toks: List[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        m = _ASCII_RUN.match(text, i) if (ch.isascii() and (ch.isalnum() or ch == "_")) else None
        if m is not None:
            toks.append(m.group())
            i = m.end()
        elif _is_cjk(ch):
            j = i
            while j < n and _is_cjk(text[j]):
                j += 1
            run = text[i:j]
            if len(run) == 1:
                toks.append(run)
            else:
                toks.extend(run[k:k + 2] for k in range(len(run) - 1))
            i = j
        else:
            i += 1
    return toks


@dataclass
class Document:
    id: str
    title: str
    content: str
    # Renderer-side provenance (e.g. policy_id, category). Never indexed and never
    # shown to the agent — retrieval sees only id/title/content.
    meta: Dict = field(default_factory=dict)


class BM25Okapi:
    """The Okapi BM25 ranking function (same formula and defaults as the widely
    used ``rank_bm25.BM25Okapi``): idf = ln((N - n + 0.5) / (n + 0.5)), with
    negative idfs floored to ``epsilon * average_idf``."""

    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75,
                 epsilon: float = 0.25):
        self.k1, self.b = k1, b
        self.corpus_size = len(corpus)
        self.doc_len = [len(d) for d in corpus]
        self.avgdl = (sum(self.doc_len) / self.corpus_size) if self.corpus_size else 0.0
        self.doc_freqs: List[Dict[str, int]] = []
        nd: Dict[str, int] = {}
        for doc in corpus:
            freqs: Dict[str, int] = {}
            for w in doc:
                freqs[w] = freqs.get(w, 0) + 1
            self.doc_freqs.append(freqs)
            for w in freqs:
                nd[w] = nd.get(w, 0) + 1
        self.idf: Dict[str, float] = {}
        idf_sum, negative = 0.0, []
        for w, f in nd.items():
            idf = math.log(self.corpus_size - f + 0.5) - math.log(f + 0.5)
            self.idf[w] = idf
            idf_sum += idf
            if idf < 0:
                negative.append(w)
        avg_idf = (idf_sum / len(self.idf)) if self.idf else 0.0
        for w in negative:
            self.idf[w] = epsilon * avg_idf

    def get_scores(self, query: List[str]) -> List[float]:
        scores = [0.0] * self.corpus_size
        for q in query:
            idf = self.idf.get(q)
            if idf is None:
                continue
            for i, freqs in enumerate(self.doc_freqs):
                f = freqs.get(q, 0)
                if f == 0:
                    continue
                denom = f + self.k1 * (1 - self.b + self.b * self.doc_len[i] / (self.avgdl or 1))
                scores[i] += idf * (f * (self.k1 + 1)) / denom
        return scores


class KnowledgeBase:
    TOP_K = 10

    def __init__(self, docs: List[Document]):
        self.docs = list(docs)
        self._bm25 = BM25Okapi([_tokenize(d.content) for d in self.docs]) if self.docs else None

    # -- the two fixed retrieval tools -------------------------------------- #
    def search(self, query: str) -> str:
        """BM25 search over document content; top 10 full documents."""
        if not query or not query.strip() or self._bm25 is None:
            return "No relevant documents found."
        scores = self._bm25.get_scores(_tokenize(query))
        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[: self.TOP_K]
        hits = [(self.docs[i], float(scores[i])) for i in top]
        if not hits:
            return "No relevant documents found."
        return self._format(hits)

    def grep(self, pattern: str) -> str:
        """Regex search over document content (case-insensitive); ranked by match count."""
        if not pattern or not pattern.strip():
            return f"No matches found for pattern: {pattern}"
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error:
            rx = re.compile(re.escape(pattern), re.IGNORECASE)
        hits: List[Tuple[Document, float]] = []
        for d in self.docs:
            n = len(rx.findall(d.content))
            if n:
                hits.append((d, float(n)))
        if not hits:
            return f"No matches found for pattern: {pattern}"
        hits.sort(key=lambda x: x[1], reverse=True)
        return self._format(hits[: self.TOP_K])

    @staticmethod
    def _format(hits: List[Tuple[Document, float]]) -> str:
        return "\n".join(
            f"{i}. {d.title}\n   ID: {d.id}\n   Score: {score:.4f}\n   Content: {d.content}\n"
            for i, (d, score) in enumerate(hits, 1)
        )

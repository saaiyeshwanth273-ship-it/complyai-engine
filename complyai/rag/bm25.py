"""BM25 (Best Matching 25) Keyword Retrieval for exact legal terms, section numbers, and statutory phrasing.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Dict, List, Tuple


class BM25Index:
    """Inverted Index implementing BM25 ranking algorithm."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: Dict[str, int] = {}
        self.doc_term_freqs: Dict[str, Counter] = {}
        self.inverted_index: Dict[str, List[str]] = {}  # term -> [doc_ids]
        self.doc_metadata: Dict[str, Any] = {}

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        return tokens

    def add_document(self, doc_id: str, text: str, metadata: Any = None) -> None:
        tokens = self._tokenize(text)
        length = len(tokens)
        self.doc_lengths[doc_id] = length
        tf = Counter(tokens)
        self.doc_term_freqs[doc_id] = tf
        if metadata:
            self.doc_metadata[doc_id] = metadata

        for term in tf.keys():
            if term not in self.inverted_index:
                self.inverted_index[term] = []
            if doc_id not in self.inverted_index[term]:
                self.inverted_index[term].append(doc_id)

        self.corpus_size = len(self.doc_lengths)
        self.avg_doc_len = sum(self.doc_lengths.values()) / max(1, self.corpus_size)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens or self.corpus_size == 0:
            return []

        scores: Dict[str, float] = {}
        for token in set(query_tokens):
            if token not in self.inverted_index:
                continue

            doc_list = self.inverted_index[token]
            n_q = len(doc_list)
            # IDF with standard floor
            idf = math.log(max(1e-6, (self.corpus_size - n_q + 0.5) / (n_q + 0.5) + 1.0))

            for doc_id in doc_list:
                f_qd = self.doc_term_freqs[doc_id][token]
                doc_len = self.doc_lengths[doc_id]
                num = f_qd * (self.k1 + 1.0)
                den = f_qd + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                term_score = idf * (num / max(1e-6, den))
                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(doc_id, score, self.doc_metadata.get(doc_id)) for doc_id, score in sorted_docs]


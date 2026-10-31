"""Regulatory Cross-Ranking and Score Calibration layer.
Weights legal hierarchy, verified source status, and exact statutory term matches.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
from complyai.types import LegalDocument, LegalSection, SourceHierarchy, SourceStatus


class RegulatoryReranker:
    """Reranks candidate legal sections incorporating authoritative source hierarchy."""

    def __init__(self, top_n: int = 10):
        self.top_n = top_n

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[LegalSection, float, LegalDocument]],
        top_k: Optional[int] = None,
    ) -> List[Tuple[LegalSection, float, LegalDocument]]:
        """Reranks candidates by combining dense similarity with statutory authority weights."""
        if not candidates:
            return []

        limit = top_k if top_k is not None else self.top_n
        q_terms = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query.lower()))
        reranked: List[Tuple[LegalSection, float, LegalDocument]] = []

        for sec, initial_score, doc in candidates:
            score = initial_score

            # 1. Hierarchy Boost (Level 1 Legislation gets higher priority than secondary commentary)
            if doc.hierarchy == SourceHierarchy.LEVEL_1_OFFICIAL_LEGISLATION:
                score *= 1.25
            elif doc.hierarchy == SourceHierarchy.LEVEL_2_OFFICIAL_REGULATOR:
                score *= 1.15
            elif doc.hierarchy == SourceHierarchy.LEVEL_4_OFFICIAL_GOV_GUIDANCE:
                score *= 1.05
            elif doc.hierarchy == SourceHierarchy.LEVEL_7_GENERAL_WEB:
                score *= 0.60

            # 2. Status verification
            if doc.status == SourceStatus.VERIFIED:
                score *= 1.10
            elif doc.status in (SourceStatus.SUPERSEDED, SourceStatus.REPEALED):
                score *= 0.20  # Penalize obsolete law

            # 3. Exact term coverage in section title and text
            sec_text = (sec.title + " " + sec.text).lower()
            overlap = sum(1 for t in q_terms if t in sec_text)
            coverage_boost = 1.0 + (0.10 * overlap)
            score *= coverage_boost

            reranked.append((sec, round(score, 4), doc))

        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:limit]

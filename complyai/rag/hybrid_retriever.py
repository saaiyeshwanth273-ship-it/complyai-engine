"""Hybrid Regulatory Retriever combining Vector Search, BM25 Keyword Search, Metadata Filtering, and Reranking.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from complyai.db.repository import RegulatoryRepository
from complyai.rag.bm25 import BM25Index
from complyai.rag.embeddings import EmbeddingService
from complyai.rag.query_router import LegalQueryRouter, RoutedQuery
from complyai.rag.reranker import RegulatoryReranker
from complyai.types import LegalDocument, LegalSection, SourceHierarchy, SourceStatus


class HybridRegulatoryRetriever:
    """Production hybrid retrieval engine for statutory and regulatory provisions."""

    def __init__(
        self,
        repository: RegulatoryRepository,
        embedding_service: Optional[EmbeddingService] = None,
        router: Optional[LegalQueryRouter] = None,
        reranker: Optional[RegulatoryReranker] = None,
    ):
        self.repository = repository
        self.embedding_service = embedding_service or EmbeddingService()
        self.router = router or LegalQueryRouter()
        self.reranker = reranker or RegulatoryReranker()
        self.bm25 = BM25Index()
        self._rebuild_bm25_index()

    def _rebuild_bm25_index(self) -> None:
        """Indexes all existing sections in repository into BM25."""
        for doc in self.repository.list_documents():
            for sec in doc.sections:
                combined_text = f"{doc.title} {sec.section_number} {sec.title} {sec.text}"
                self.bm25.add_document(
                    doc_id=sec.section_id,
                    text=combined_text,
                    metadata={"doc_id": doc.document_id, "section": sec},
                )

    def retrieve(
        self,
        query: str,
        business_context: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        target_jurisdiction: Optional[str] = None,
        min_hierarchy: Optional[SourceHierarchy] = SourceHierarchy.LEVEL_5_RECOGNIZED_LEGAL_DATABASE,
    ) -> List[Tuple[LegalSection, float, LegalDocument]]:
        """Executes Hybrid retrieval: Query routing -> Vector search + BM25 search -> Reciprocal Rank Fusion -> Reranker."""
        # Refresh BM25 if repository has more sections
        if self.bm25.corpus_size < len(self.repository._sections):
            self._rebuild_bm25_index()

        # 1. Route query
        routed: RoutedQuery = self.router.route_query(query, business_context)
        jurisdiction = target_jurisdiction or (routed.jurisdictions[0] if routed.jurisdictions else None)

        # 2. Dense Vector Search
        q_vec = self.embedding_service.embed_text(query)
        vector_candidates = self.repository.search_sections_vector(
            query_embedding=q_vec,
            top_k=top_k * 2,
            jurisdiction=jurisdiction,
            min_hierarchy=min_hierarchy,
            only_verified=True,
        )

        # 3. Sparse BM25 Keyword Search
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        # 4. Fusion of dense and sparse candidates
        candidate_dict: Dict[str, Tuple[LegalSection, float, LegalDocument]] = {}

        # Add vector results
        for sec, sim_score, doc in vector_candidates:
            candidate_dict[sec.section_id] = (sec, sim_score, doc)

        # Blend BM25 results
        for sec_id, bm_score, meta in bm25_results:
            sec = self.repository.get_section(sec_id)
            if not sec:
                continue
            doc_id = sec_id.split("::")[0] if "::" in sec_id else None
            doc = self.repository.get_document(doc_id) if doc_id else None
            if not doc:
                continue
            if jurisdiction and jurisdiction.lower() not in doc.jurisdiction.lower():
                continue

            # Normalize BM25 score approximately into [0, 1] range
            norm_bm = min(1.0, bm_score / 15.0)
            if sec.section_id in candidate_dict:
                existing_sec, existing_score, existing_doc = candidate_dict[sec.section_id]
                fused_score = (existing_score * 0.6) + (norm_bm * 0.4)
                candidate_dict[sec.section_id] = (sec, fused_score, doc)
            else:
                candidate_dict[sec.section_id] = (sec, norm_bm * 0.5, doc)

        candidates = list(candidate_dict.values())

        # 5. Authoritative Reranking
        reranked = self.reranker.rerank(query=query, candidates=candidates, top_k=top_k)
        return reranked[:top_k]

    def build_regulatory_context(
        self,
        retrieved: List[Tuple[LegalSection, float, LegalDocument]],
    ) -> str:
        """Formats verified regulatory text into strict citation-grounded context for Gemma."""
        if not retrieved:
            return "NO_VERIFIED_REGULATORY_SOURCES_AVAILABLE"

        lines = ["=== AUTHORITATIVE REGULATORY CONTEXT ==="]
        for sec, score, doc in retrieved:
            lines.append(f"\n[SOURCE_ID: {doc.document_id}]")
            lines.append(f"Title: {doc.title} ({doc.short_title})")
            lines.append(f"Jurisdiction: {doc.jurisdiction}")
            lines.append(f"Authority: {doc.authority}")
            lines.append(f"Instrument Type: {doc.instrument_type.value}")
            lines.append(f"Section: {sec.section_number} - {sec.title}")
            lines.append(f"Official Source URL: {doc.source_url}")
            lines.append(f"Effective Date: {doc.effective_date}")
            lines.append(f"Verified Text: {sec.text}")
            if sec.requirements:
                lines.append("Extracted Statutory Requirements:")
                for r in sec.requirements:
                    lines.append(f"  * {r.obligation} (Subject: {r.subject})")
            lines.append("---")
        lines.append("=== END OF AUTHORITATIVE CONTEXT ===")
        return "\n".join(lines)

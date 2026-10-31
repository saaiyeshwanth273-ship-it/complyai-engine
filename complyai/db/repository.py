"""Database repository and in-memory/SQLite compliant store for ComplyAI.
Provides fast vector similarity retrieval, metadata filtering, and full source lifecycle.
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from complyai.types import (
    Citation,
    ComplianceFinding,
    InstrumentType,
    LegalDocument,
    LegalDomain,
    LegalRequirement,
    LegalSection,
    RiskLevel,
    SourceHierarchy,
    SourceStatus,
)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class RegulatoryRepository:
    """In-memory & SQLite backed repository for regulatory sources, sections, requirements."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._sources: Dict[str, LegalDocument] = {}
        self._sections: Dict[str, LegalSection] = {}
        self._requirements: Dict[str, LegalRequirement] = {}
        self._section_embeddings: Dict[str, List[float]] = {}
        self._requirement_embeddings: Dict[str, List[float]] = {}
        self._definitions: Dict[str, Dict[str, str]] = {}  # term -> {doc_id, def, section}
        self._audit_logs: Dict[str, Dict[str, Any]] = {}
        self._reviewer_feedback: List[Dict[str, Any]] = []

    def add_document(self, doc: LegalDocument) -> None:
        """Stores a legal document and indexes its sections and requirements."""
        if not doc.checksum:
            doc.checksum = hashlib.sha256(doc.title.encode("utf-8")).hexdigest()
        self._sources[doc.document_id] = doc

        for sec in doc.sections:
            self._sections[sec.section_id] = sec
            # Index definitions
            for term, definition in sec.definitions.items():
                self._definitions[term.lower()] = {
                    "document_id": doc.document_id,
                    "term": term,
                    "definition": definition,
                    "section": sec.section_number,
                }
            for req in sec.requirements:
                # Ensure parent attributes are propagated
                if not req.source_id:
                    req.source_id = doc.document_id
                if not req.source_title:
                    req.source_title = doc.title
                if not req.jurisdiction:
                    req.jurisdiction = doc.jurisdiction
                if not req.authority:
                    req.authority = doc.authority
                self._requirements[req.requirement_id] = req

    def get_document(self, document_id: str) -> Optional[LegalDocument]:
        return self._sources.get(document_id)

    def list_documents(
        self,
        jurisdiction: Optional[str] = None,
        domain: Optional[LegalDomain] = None,
        status: Optional[SourceStatus] = None,
    ) -> List[LegalDocument]:
        results = list(self._sources.values())
        if jurisdiction:
            results = [d for d in results if jurisdiction.lower() in d.jurisdiction.lower()]
        if domain:
            results = [d for d in results if d.domain == domain]
        if status:
            results = [d for d in results if d.status == status]
        return results

    def get_section(self, section_id: str) -> Optional[LegalSection]:
        return self._sections.get(section_id)

    def get_requirement(self, requirement_id: str) -> Optional[LegalRequirement]:
        return self._requirements.get(requirement_id)

    def set_section_embedding(self, section_id: str, embedding: List[float]) -> None:
        self._section_embeddings[section_id] = embedding

    def set_requirement_embedding(self, requirement_id: str, embedding: List[float]) -> None:
        self._requirement_embeddings[requirement_id] = embedding

    def search_sections_vector(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        min_hierarchy: Optional[SourceHierarchy] = None,
        only_verified: bool = True,
    ) -> List[Tuple[LegalSection, float, LegalDocument]]:
        """Vector semantic search over sections with regulatory metadata filtering."""
        scored: List[Tuple[LegalSection, float, LegalDocument]] = []
        for sec_id, emb in self._section_embeddings.items():
            sec = self._sections.get(sec_id)
            if not sec:
                continue
            doc_id = sec_id.split("::")[0] if "::" in sec_id else None
            doc = self._sources.get(doc_id) if doc_id else None
            if not doc:
                # search by matching section
                for d in self._sources.values():
                    if any(s.section_id == sec_id for s in d.sections):
                        doc = d
                        break
            if not doc:
                continue

            if only_verified and doc.status != SourceStatus.VERIFIED:
                continue
            if jurisdiction and jurisdiction.lower() not in doc.jurisdiction.lower():
                continue
            if min_hierarchy and doc.hierarchy > min_hierarchy:
                continue

            sim = cosine_similarity(query_embedding, emb)
            scored.append((sec, sim, doc))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def search_requirements(
        self,
        jurisdiction: Optional[str] = None,
        domain: Optional[LegalDomain] = None,
        subject: Optional[str] = None,
    ) -> List[LegalRequirement]:
        reqs = list(self._requirements.values())
        if jurisdiction:
            reqs = [r for r in reqs if jurisdiction.lower() in r.jurisdiction.lower()]
        if subject:
            reqs = [r for r in reqs if subject.lower() in r.subject.lower()]
        return reqs

    def resolve_definition(self, term: str) -> Optional[Dict[str, str]]:
        return self._definitions.get(term.strip().lower())

    def save_audit_log(self, audit_id: str, payload: Dict[str, Any]) -> None:
        self._audit_logs[audit_id] = payload

    def get_audit_log(self, audit_id: str) -> Optional[Dict[str, Any]]:
        return self._audit_logs.get(audit_id)

    def record_reviewer_feedback(self, feedback: Dict[str, Any]) -> None:
        self._reviewer_feedback.append(feedback)

    def get_all_reviewer_feedback(self) -> List[Dict[str, Any]]:
        return list(self._reviewer_feedback)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self._sources),
            "verified_documents": sum(1 for d in self._sources.values() if d.status == SourceStatus.VERIFIED),
            "total_sections": len(self._sections),
            "total_requirements": len(self._requirements),
            "total_definitions": len(self._definitions),
            "total_audits_logged": len(self._audit_logs),
        }


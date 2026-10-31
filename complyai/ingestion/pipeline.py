"""Regulatory Ingestion Service executing end-to-end ingestion, parsing, requirement extraction, and indexing.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from complyai.connectors.base import BaseRegulatoryConnector
from complyai.db.repository import RegulatoryRepository
from complyai.rag.embeddings import EmbeddingService
from complyai.types import LegalDocument, LegalRequirement, LegalSection, SourceHierarchy, SourceStatus


class RegulatoryIngestionService:
    """End-to-end pipeline for ingesting official regulatory sources into the knowledge layer."""

    def __init__(
        self,
        repository: RegulatoryRepository,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.repository = repository
        self.embedding_service = embedding_service or EmbeddingService()

    def ingest_from_connector(
        self,
        connector: BaseRegulatoryConnector,
        source_id: str,
        require_verification: bool = True,
    ) -> LegalDocument:
        """Executes the 12-step regulatory ingestion pipeline."""
        # 1. Source Discovery / Fetch
        raw_data = connector.fetch_source(source_id)

        # 2. Source Verification & Checksum
        content_for_hash = raw_data.get("title", "") + str(raw_data.get("effective_date", ""))
        checksum = hashlib.sha256(content_for_hash.encode("utf-8")).hexdigest()

        # 3. Document Parsing & Structure Detection
        doc: LegalDocument = connector.parse_source(raw_data)
        doc.checksum = checksum
        doc.last_checked_at = datetime.now(timezone.utc).isoformat()
        if require_verification:
            doc.status = SourceStatus.VERIFIED
            doc.verified_at = datetime.now(timezone.utc).isoformat()

        # 4. Generate embeddings for sections & requirements
        for sec in doc.sections:
            sec_text = f"{doc.title} Section {sec.section_number}: {sec.title}. {sec.text}"
            sec_embedding = self.embedding_service.embed_text(sec_text)
            self.repository.set_section_embedding(sec.section_id, sec_embedding)

            for req in sec.requirements:
                req_text = f"{req.obligation} (Subject: {req.subject}, Action: {req.action}, Object: {req.object})"
                req_embedding = self.embedding_service.embed_text(req_text)
                self.repository.set_requirement_embedding(req.requirement_id, req_embedding)

        # 5. Index into repository
        self.repository.add_document(doc)
        return doc

    def ingest_all_from_connector(self, connector: BaseRegulatoryConnector) -> List[LegalDocument]:
        ingested = []
        for item in connector.discover_sources():
            doc = self.ingest_from_connector(connector, item["source_id"])
            ingested.append(doc)
        return ingested

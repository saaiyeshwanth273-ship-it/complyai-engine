"""Regulatory Freshness & Change Detection Monitor.
Tracks gazettes, circulars, and amendments; performs impact analysis on active compliance audits.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from complyai.connectors.base import BaseRegulatoryConnector
from complyai.db.repository import RegulatoryRepository
from complyai.types import LegalDocument, SourceStatus


@dataclass
class ChangeImpactReport:
    document_id: str
    statute_title: str
    change_type: str  # AMENDMENT, REPEAL, NOTIFICATION, GUIDANCE_UPDATE
    previous_hash: str
    new_hash: str
    affected_requirements: List[str] = field(default_factory=list)
    affected_compliance_controls: List[str] = field(default_factory=list)
    recommended_audit_actions: List[str] = field(default_factory=list)
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RegulatoryChangeMonitor:
    """Monitors regulatory sources for legal changes and conducts change impact analysis."""

    def __init__(self, repository: RegulatoryRepository):
        self.repository = repository

    def check_for_updates(
        self,
        connector: BaseRegulatoryConnector,
        source_id: str,
    ) -> Optional[ChangeImpactReport]:
        existing_doc = self.repository.get_document(source_id)
        if not existing_doc:
            return None

        change_info = connector.detect_changes(source_id, existing_doc.checksum)
        if not change_info.get("changed"):
            return None

        # Change detected! Execute change impact analysis
        affected_reqs = [r.requirement_id for s in existing_doc.sections for r in s.requirements]
        affected_controls = [f"Control {r.object}" for s in existing_doc.sections for r in s.requirements]

        return ChangeImpactReport(
            document_id=source_id,
            statute_title=existing_doc.title,
            change_type="AMENDMENT",
            previous_hash=existing_doc.checksum,
            new_hash=change_info.get("current_hash", ""),
            affected_requirements=affected_reqs,
            affected_compliance_controls=affected_controls,
            recommended_audit_actions=[
                f"Notify compliance officers managing {existing_doc.short_title}.",
                "Trigger automated re-audit for organizations operating under this jurisdiction.",
                "Review updated statutory text and obtain professional legal review.",
            ],
        )

    def evaluate_freshness(self, doc: LegalDocument) -> Dict[str, Any]:
        """Calculates freshness status of an authoritative regulatory document."""
        needs_verification = False
        reasons = []

        if not doc.verified_at:
            needs_verification = True
            reasons.append("Document has never been formally verified by admin.")

        if doc.status == SourceStatus.PENDING_REVIEW:
            needs_verification = True
            reasons.append("Document is pending legal administrator review.")

        return {
            "document_id": doc.document_id,
            "title": doc.title,
            "status": doc.status.value,
            "version": doc.version,
            "effective_date": doc.effective_date,
            "last_verified": doc.verified_at or "NEVER",
            "freshness": "REQUIRES_VERIFICATION" if needs_verification else "FRESH",
            "reasons": reasons,
        }

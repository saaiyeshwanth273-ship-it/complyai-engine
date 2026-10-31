"""Temporal Legal Reasoning Engine.
Ensures compliance audits evaluate historical documents against the law effective AT THAT SPECIFIC TIME,
preventing anachronistic application of newer statutes or repealed provisions.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from complyai.types import LegalDocument, SourceStatus


class TemporalReasoningEngine:
    """Evaluates the temporal validity of statutes and regulations against document or event dates."""

    def _parse_date(self, d_str: Optional[str]) -> Optional[date]:
        if not d_str:
            return None
        # Handle ISO format or standard YYYY-MM-DD
        d_clean = d_str.split("T")[0]
        try:
            return datetime.strptime(d_clean, "%Y-%m-%d").date()
        except ValueError:
            return None

    def is_effective_at(self, doc: LegalDocument, target_date_str: str) -> Dict[str, Any]:
        """Checks if a legal document or section was legally in force on target_date_str."""
        target_date = self._parse_date(target_date_str)
        if not target_date:
            return {
                "in_force": True,
                "confidence": 0.70,
                "reason": f"Unable to parse document date '{target_date_str}'. Defaulting to current applicability.",
            }

        effective_date = self._parse_date(doc.effective_date)
        repealed_date = self._parse_date(doc.repealed_date)

        # 1. Before effective date
        if effective_date and target_date < effective_date:
            return {
                "in_force": False,
                "status": "FUTURE_LAW_AT_DATE",
                "confidence": 0.98,
                "reason": (
                    f"Document date ({target_date}) predates the effective date "
                    f"of {doc.short_title} ({effective_date}). This statute cannot be used to judge conduct before it took effect."
                ),
            }

        # 2. After repealed date
        if repealed_date and target_date >= repealed_date:
            return {
                "in_force": False,
                "status": "REPEALED_AT_DATE",
                "confidence": 0.98,
                "reason": (
                    f"Document date ({target_date}) is after {doc.short_title} was repealed on {repealed_date}."
                ),
            }

        # 3. Document was in force
        return {
            "in_force": True,
            "status": "IN_FORCE",
            "confidence": 0.96,
            "reason": f"{doc.short_title} was in force on {target_date}.",
        }

    def filter_documents_by_date(
        self,
        docs: List[LegalDocument],
        document_date_str: str,
    ) -> List[LegalDocument]:
        """Returns only legal documents that were effective on document_date_str."""
        valid_docs = []
        for d in docs:
            check = self.is_effective_at(d, document_date_str)
            if check["in_force"]:
                valid_docs.append(d)
        return valid_docs


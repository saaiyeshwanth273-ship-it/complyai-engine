"""Citation Validator verifying every statutory reference, section, URL, and quoted excerpt against authoritative database.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from complyai.db.repository import RegulatoryRepository
from complyai.types import Citation, SourceStatus


@dataclass
class CitationVerificationResult:
    citation: Citation
    is_valid: bool
    status: str  # VALID, INVALID_SOURCE_NOT_FOUND, INVALID_SECTION, INVALID_QUOTE_MISMATCH, UNVERIFIED_SOURCE_STATUS
    notes: str
    match_score: float


class CitationValidator:
    """Verifies that generated citations reference real, verified statutory documents in the repository."""

    def __init__(self, repository: RegulatoryRepository, min_quote_overlap: float = 0.65):
        self.repository = repository
        self.min_quote_overlap = min_quote_overlap

    def verify_citation(self, citation: Citation) -> CitationVerificationResult:
        # 1. Source existence check
        doc = self.repository.get_document(citation.source_id)
        if not doc:
            # Try searching by title
            for d in self.repository.list_documents():
                if citation.title and (citation.title.lower() in d.title.lower() or d.short_title.lower() in citation.title.lower()):
                    doc = d
                    break

        if not doc:
            return CitationVerificationResult(
                citation=citation,
                is_valid=False,
                status="INVALID_SOURCE_NOT_FOUND",
                notes=f"Statutory document '{citation.source_id}' / '{citation.title}' does not exist in authoritative database.",
                match_score=0.0,
            )

        # 2. Source status check (Must be VERIFIED)
        if doc.status != SourceStatus.VERIFIED:
            return CitationVerificationResult(
                citation=citation,
                is_valid=False,
                status="UNVERIFIED_SOURCE_STATUS",
                notes=f"Source '{doc.short_title}' has status '{doc.status.value}'. Only VERIFIED sources can be cited for compliance findings.",
                match_score=0.4,
            )

        # 3. URL validity check
        if not doc.source_url or not doc.source_url.startswith("http"):
            return CitationVerificationResult(
                citation=citation,
                is_valid=False,
                status="INVALID_URL",
                notes="Authoritative document lacks a valid official source URL.",
                match_score=0.5,
            )

        # 4. Section verification
        target_sec = None
        clean_target = citation.section.lower().replace("section", "").replace("article", "").strip()
        for s in doc.sections:
            clean_s = s.section_number.lower().replace("section", "").replace("article", "").strip()
            if clean_target == clean_s or clean_target in clean_s or clean_s in clean_target:
                target_sec = s
                break

        if not target_sec:
            # Section does not exist in statute
            return CitationVerificationResult(
                citation=citation,
                is_valid=False,
                status="INVALID_SECTION",
                notes=f"Section '{citation.section}' does not exist in verified document '{doc.short_title}'.",
                match_score=0.3,
            )

        # 5. Quoted text verification
        quoted = citation.quoted_text.strip()
        if quoted:
            # Check overlap between quoted text and actual section text
            quoted_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", quoted.lower()))
            sec_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", target_sec.text.lower()))

            if quoted_words:
                overlap = len(quoted_words.intersection(sec_words)) / len(quoted_words)
                if overlap < self.min_quote_overlap:
                    return CitationVerificationResult(
                        citation=citation,
                        is_valid=False,
                        status="INVALID_QUOTE_MISMATCH",
                        notes=f"Quoted text overlap ({overlap:.1%}) is below threshold ({self.min_quote_overlap:.1%}) with verified text in Section {target_sec.section_number}.",
                        match_score=overlap,
                    )
                match_score = overlap
            else:
                match_score = 0.95
        else:
            match_score = 0.90

        # Mark citation as verified
        citation.verified = True
        citation.verification_notes = f"Verified against official text of {doc.title} ({target_sec.section_number})."

        return CitationVerificationResult(
            citation=citation,
            is_valid=True,
            status="VALID",
            notes=citation.verification_notes,
            match_score=match_score,
        )

    def verify_all(self, citations: List[Citation]) -> List[CitationVerificationResult]:
        return [self.verify_citation(c) for c in citations]


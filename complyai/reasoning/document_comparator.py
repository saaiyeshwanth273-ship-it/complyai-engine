"""Document-to-Law Comparison Engine.
Compares statutory legal requirements against observed clauses in business documents to identify potential gaps.
Follows the structured pipeline:
LEGAL REQUIREMENT -> EXPECTED CONTROL -> BUSINESS DOCUMENT -> OBSERVED CONTROL -> POTENTIAL GAP
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from complyai.reasoning.definitions import ExtractedClause
from complyai.types import LegalRequirement


@dataclass
class ComparisonFinding:
    requirement_id: str
    requirement_text: str
    expected_control: str
    observed_control: Optional[str]
    has_potential_gap: bool
    evidence_text: Optional[str]
    gap_summary: str
    confidence: float


class DocumentComparator:
    """Executes structured comparison between verified statutory requirements and business documents."""

    def compare_requirement_against_clauses(
        self,
        requirement: LegalRequirement,
        clauses: List[ExtractedClause],
    ) -> ComparisonFinding:
        expected_control = f"Document must establish or reflect: {requirement.obligation}"

        # Match relevant clauses based on keywords in requirement
        req_terms = set(re.findall(r"\b[a-zA-Z]{4,}\b", (requirement.obligation + " " + requirement.object).lower()))
        matched_clauses: List[ExtractedClause] = []

        for cl in clauses:
            cl_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", cl.text.lower()))
            overlap = req_terms.intersection(cl_words)
            if len(overlap) >= 2 or any(term in cl.text.lower() for term in [requirement.object.lower()]):
                matched_clauses.append(cl)

        if not matched_clauses:
            # Complete absence of required provision
            return ComparisonFinding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.obligation,
                expected_control=expected_control,
                observed_control=None,
                has_potential_gap=True,
                evidence_text=None,
                gap_summary=(
                    f"Document does not appear to contain an explicit provision for: '{requirement.object}'. "
                    f"Potential compliance gap requiring review against {requirement.source_title} ({requirement.source_section})."
                ),
                confidence=0.88,
            )

        # Check if the matched clauses adequately fulfill the obligation
        best_clause = matched_clauses[0]
        cl_text_lower = best_clause.text.lower()

        # Check for specific deadlines or conditions
        deadline_missing = False
        if requirement.deadline:
            d_terms = re.findall(r"\b\d+\s*(?:hours|days|months)\b", requirement.deadline.lower())
            for d in d_terms:
                if d not in cl_text_lower:
                    deadline_missing = True
                    break

        if deadline_missing:
            return ComparisonFinding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.obligation,
                expected_control=expected_control,
                observed_control=best_clause.text,
                has_potential_gap=True,
                evidence_text=best_clause.text,
                gap_summary=(
                    f"Clause addresses '{requirement.object}' but does not explicitly reflect the statutory timeframe: "
                    f"'{requirement.deadline}'. Potential compliance gap requiring review."
                ),
                confidence=0.91,
            )

        # Adequate alignment observed
        return ComparisonFinding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.obligation,
            expected_control=expected_control,
            observed_control=best_clause.text,
            has_potential_gap=False,
            evidence_text=best_clause.text,
            gap_summary="Provision appears to address the statutory requirement based on available text.",
            confidence=0.90,
        )


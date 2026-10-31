"""Legal Definitions Resolver and Document Clause Analyzer.
Extracts contract/policy clauses and resolves statutory definitions over generic dictionary terms.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from complyai.db.repository import RegulatoryRepository


@dataclass
class ExtractedClause:
    clause_id: str
    clause_type: str  # TERMINATION, NOTICE, DATA_PROTECTION, CONFIDENTIALITY, LEAVE, WORKING_HOURS, LIABILITIES
    heading: str
    text: str
    obligations: List[str] = field(default_factory=list)


class LegalDefinitionResolver:
    """Resolves statutory definitions from authoritative legal documents."""

    def __init__(self, repository: RegulatoryRepository):
        self.repository = repository

    def resolve(self, term: str, jurisdiction: str = "India") -> Optional[Dict[str, str]]:
        """Retrieves verified statutory definition for terms like 'employee', 'worker', 'data fiduciary'."""
        result = self.repository.resolve_definition(term)
        return result


class DocumentClauseAnalyzer:
    """Analyzes business documents (HR policies, vendor agreements, privacy notices, codes of conduct)
    and extracts standard legal clauses.
    """

    def __init__(self):
        self.clause_patterns = {
            "DATA_PROTECTION": [r"personal data", r"privacy", r"security safeguards", r"data protection", r"confidential information"],
            "LEAVE_AND_HOURS": [r"leave", r"vacation", r"working hours", r"overtime", r"weekly off"],
            "TERMINATION": [r"termination", r"notice period", r"severance", r"dismissal", r"resignation"],
            "WORKPLACE_SAFETY": [r"sexual harassment", r"complaints committee", r"icc", r"posh", r"safety", r"health"],
            "COMPENSATION": [r"salary", r"wages", r"bonus", r"pf", r"provident fund", r"gratuity"],
            "INCIDENT_RESPONSE": [r"incident", r"breach notification", r"cert-in", r"security event"],
        }

    def extract_clauses(self, document_text: str) -> List[ExtractedClause]:
        paragraphs = [p.strip() for p in document_text.split("\n\n") if p.strip()]
        extracted: List[ExtractedClause] = []

        for idx, p in enumerate(paragraphs):
            matched_type = "GENERAL_PROVISION"
            for c_type, patterns in self.clause_patterns.items():
                if any(re.search(pat, p, re.IGNORECASE) for pat in patterns):
                    matched_type = c_type
                    break

            # Infer heading or use first 6 words
            lines = p.split("\n")
            heading = lines[0][:80] if len(lines) > 1 else p[:50] + "..."

            extracted.append(
                ExtractedClause(
                    clause_id=f"CLAUSE-{idx + 1:03d}",
                    clause_type=matched_type,
                    heading=heading,
                    text=p,
                    obligations=[p],
                )
            )

        return extracted


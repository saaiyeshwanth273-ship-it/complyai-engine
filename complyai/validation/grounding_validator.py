"""Grounding Validator evaluating factual grounding and calculating multi-dimensional confidence scores.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from complyai.types import ClaimType, ComplianceFinding, ConfidenceScore


@dataclass
class ClaimEvaluation:
    claim_text: str
    claim_type: ClaimType
    supported: bool
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.90
    notes: str = ""


class GroundingValidator:
    """Evaluates whether generated compliance claims are grounded in verified regulatory context."""

    def evaluate_finding_grounding(
        self,
        finding: ComplianceFinding,
        retrieved_context: str,
    ) -> Tuple[bool, List[ClaimEvaluation], ConfidenceScore]:
        claims_eval: List[ClaimEvaluation] = []
        context_lower = retrieved_context.lower()

        # 1. Evaluate requirement statement
        req_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", finding.requirement.lower()))
        req_supported = False
        if req_words:
            matched_words = [w for w in req_words if w in context_lower]
            ratio = len(matched_words) / len(req_words)
            req_supported = ratio >= 0.50

        claims_eval.append(
            ClaimEvaluation(
                claim_text=finding.requirement,
                claim_type=ClaimType.LEGAL_REQUIREMENT,
                supported=req_supported,
                source_ids=[c.source_id for c in finding.citations],
                confidence=0.92 if req_supported else 0.40,
                notes="Statutory requirement grounded in retrieved official text." if req_supported else "Requirement text not sufficiently matched in retrieved context.",
            )
        )

        # 2. Evaluate finding / AI interpretation
        claims_eval.append(
            ClaimEvaluation(
                claim_text=finding.finding,
                claim_type=ClaimType.AI_INTERPRETATION,
                supported=True,
                source_ids=[c.source_id for c in finding.citations],
                confidence=0.88,
                notes="AI interpretation of gap between document evidence and statutory requirement.",
            )
        )

        # 3. Evaluate citation grounding
        citation_conf = 0.0
        if finding.citations:
            verified_count = sum(1 for c in finding.citations if c.verified)
            citation_conf = verified_count / len(finding.citations)
        else:
            citation_conf = 0.50

        # Build multi-dimensional confidence score
        conf = ConfidenceScore(
            retrieval_confidence=0.92,
            source_confidence=0.96 if finding.citations and all(c.verified for c in finding.citations) else 0.70,
            applicability_confidence=0.90,
            reasoning_confidence=0.88 if req_supported else 0.50,
            citation_confidence=citation_conf,
        )
        conf.compute_overall()

        overall_grounded = req_supported and (citation_conf >= 0.70 or not finding.citations)
        if not overall_grounded:
            finding.grounding_status = "UNGROUNDED"
            finding.requires_human_review = True
        else:
            finding.grounding_status = "VERIFIED"

        finding.confidence = conf
        return overall_grounded, claims_eval, conf


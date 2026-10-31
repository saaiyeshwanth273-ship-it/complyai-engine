"""Compliance Risk Engine for calculating severity, likelihood, and regulatory exposure scores.
The score is an internal prioritization metric, not a definitive legal adjudication.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from complyai.types import ConfidenceScore, LegalRequirement, RiskLevel


class RiskEngine:
    """Calculates prioritized compliance risk score [0 - 100] based on regulatory exposure,
    impact, source hierarchy, and applicability confidence.
    """

    def calculate_risk(
        self,
        has_gap: bool,
        requirement: LegalRequirement,
        business_exposure_factor: float = 1.0,
        confidence: Optional[ConfidenceScore] = None,
    ) -> Dict[str, Any]:
        if not has_gap:
            return {
                "severity": RiskLevel.LOW,
                "score": 10,
                "reason": "Observed controls appear aligned with available statutory requirement.",
                "confidence": confidence.overall_confidence if confidence else 0.90,
            }

        # Base severity based on legal domain & penalty exposure
        req_obj = (requirement.obligation + " " + (requirement.penalties or "")).lower()
        base_score = 50

        # Critical triggers: cyber breach reporting, sexual harassment committee, financial audits, child labour
        if any(w in req_obj for w in ["6 hours", "incident reporting", "cert-in", "breach"]):
            base_score = 85
        elif any(w in req_obj for w in ["posh", "sexual harassment", "internal complaints committee", "child labour"]):
            base_score = 80
        elif any(w in req_obj for w in ["consent", "data fiduciary", "reasonable security safeguards", "minimum wage"]):
            base_score = 70
        elif any(w in req_obj for w in ["register", "records", "filing", "board report"]):
            base_score = 55

        # Factor in business exposure
        adjusted_score = min(98, max(5, int(base_score * business_exposure_factor)))

        if adjusted_score >= 80:
            severity = RiskLevel.HIGH
        elif adjusted_score >= 50:
            severity = RiskLevel.MEDIUM
        else:
            severity = RiskLevel.LOW

        # If penalties mention imprisonment or severe statutory fines
        if requirement.penalties and any(p in requirement.penalties.lower() for p in ["imprisonment", "crore", "million", "penalty"]):
            if adjusted_score >= 75:
                severity = RiskLevel.HIGH

        return {
            "severity": severity,
            "score": adjusted_score,
            "reason": (
                f"Potential gap in '{requirement.object}'. "
                f"Statutory authority: {requirement.authority}. "
                f"Internal score {adjusted_score}/100 reflects exposure and enforcement priority."
            ),
            "confidence": confidence.overall_confidence if confidence else 0.88,
        }


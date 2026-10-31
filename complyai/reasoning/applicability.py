"""Applicability Engine determining whether statutes, rules, or codes apply to a specific business.
Prevents naive keyword-matching retrieval from triggering irrelevant statutory obligations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from complyai.types import BusinessProfile, LegalDocument, LegalRequirement


@dataclass
class ApplicabilityResult:
    applicable: bool
    confidence: float
    reasons: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    requires_human_review: bool = False
    territorial_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applicable": self.applicable,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "conditions": self.conditions,
            "requires_human_review": self.requires_human_review,
            "territorial_notes": self.territorial_notes,
        }


class ApplicabilityEngine:
    """Evaluates statutory applicability thresholds (headcount, turnover, sector, jurisdiction, cross-border activity)."""

    def evaluate(
        self,
        profile: BusinessProfile,
        doc: LegalDocument,
        requirement: Optional[LegalRequirement] = None,
    ) -> ApplicabilityResult:
        reasons: List[str] = []
        conditions: List[str] = []
        requires_review = False
        confidence = 0.95

        # 1. Jurisdiction Match & Cross-border Territorial Scope
        doc_jurisdiction = doc.jurisdiction.lower()
        business_country = profile.country.lower()

        # Direct domestic match
        domestic_match = business_country in doc_jurisdiction or doc_jurisdiction.startswith("india") and business_country == "india"

        # Extra-territorial / Cross-border reach check
        extra_territorial_trigger = False
        if "european union" in doc_jurisdiction or "eu" in doc_jurisdiction:
            if "EU" in profile.customers or any("eu" in s.lower() for s in profile.data_subjects_locations):
                extra_territorial_trigger = True
                reasons.append(
                    "Potential extraterritorial applicability under GDPR Article 3(2) (offering goods/services to EU data subjects or monitoring behaviour)."
                )
                conditions.append("Requires factual review of whether goods/services are actively marketed to EU residents.")
                requires_review = True
                confidence = 0.85

        if "california" in doc_jurisdiction:
            if "US" in profile.customers:
                # CCPA revenue threshold ($25M USD) or 100k consumers
                if profile.annual_revenue_usd > 25_000_000:
                    extra_territorial_trigger = True
                    reasons.append("California CCPA gross annual revenue threshold ($25M+) potentially triggered.")
                else:
                    conditions.append("California CCPA applies only if gross revenue exceeds $25M USD or collects personal info of 100k+ CA consumers.")
                    requires_review = True

        if not domestic_match and not extra_territorial_trigger:
            return ApplicabilityResult(
                applicable=False,
                confidence=0.98,
                reasons=[f"Document jurisdiction '{doc.jurisdiction}' does not apply to operations in '{profile.country}'."],
            )

        # 2. State-level check within India
        if doc.state:
            if doc.state.lower() not in [s.lower() for s in profile.states]:
                return ApplicabilityResult(
                    applicable=False,
                    confidence=0.95,
                    reasons=[f"State legislation '{doc.state}' does not match company active states {profile.states}."],
                )

        # 3. Headcount / Employee threshold evaluation
        doc_id = doc.document_id.upper()
        if "POSH" in doc_id or "SEXUAL HARASSMENT" in doc.title.upper():
            if profile.employee_count >= 10:
                reasons.append(f"Company has {profile.employee_count} employees (threshold is >= 10 workers for mandatory ICC).")
            else:
                return ApplicabilityResult(
                    applicable=False,
                    confidence=0.95,
                    reasons=[f"Company employs {profile.employee_count} workers (below 10 worker threshold for ICC constitution)."],
                )

        if "EPFO" in doc_id or "PROVIDENT FUND" in doc.title.upper():
            if profile.employee_count >= 20:
                reasons.append(f"Company has {profile.employee_count} employees (threshold is >= 20 for mandatory EPF coverage).")
            else:
                conditions.append("Voluntary coverage possible if employee count is under 20.")

        # 4. Corporate turnover & net worth thresholds (e.g. CSR Section 135 of Companies Act, 2013)
        if "135" in (requirement.source_section if requirement else "") or "CSR" in (requirement.obligation if requirement else ""):
            # Net worth >= 500 Cr (5B INR), Turnover >= 1000 Cr (10B INR), or Net Profit >= 5 Cr (50M INR)
            threshold_turnover = 10_000_000_000.0
            if profile.turnover_inr >= threshold_turnover:
                reasons.append(f"Company turnover INR {profile.turnover_inr:,.0f} meets or exceeds CSR threshold (INR 1,000 Crore).")
            else:
                return ApplicabilityResult(
                    applicable=False,
                    confidence=0.92,
                    reasons=[f"Company turnover INR {profile.turnover_inr:,.0f} is below the 1,000 Crore CSR threshold."],
                    conditions=["Check if net worth >= 500 Cr or net profit >= 5 Cr in preceding financial year."],
                    requires_human_review=True,
                )

        # 5. Cyber Security Directions (CERT-In)
        if "CERTIN" in doc_id or "CERT-IN" in doc.title.upper():
            if profile.industry.lower() in ["it", "information technology", "telecom", "finance", "cloud", "software"]:
                reasons.append("IT & software service providers are explicitly covered bodies corporate under CERT-In Directions.")

        # Default applicable if conditions passed
        if not reasons:
            reasons.append(f"Statute '{doc.short_title}' generally governs {profile.business_type} entities in {profile.country}.")

        return ApplicabilityResult(
            applicable=True,
            confidence=confidence,
            reasons=reasons,
            conditions=conditions,
            requires_human_review=requires_review,
        )


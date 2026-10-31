"""Legal Query Router for domain classification, intent detection, and targeted retrieval routing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from complyai.types import LegalDomain


@dataclass
class RoutedQuery:
    raw_query: str
    intent: str  # REGULATION_LOOKUP, DOCUMENT_ANALYSIS, COMPLIANCE_AUDIT, POLICY_REVIEW
    primary_domain: LegalDomain
    jurisdictions: List[str] = field(default_factory=lambda: ["India"])
    state: Optional[str] = None
    target_entity: Optional[str] = None  # e.g., "Employer", "Data Fiduciary"
    topic: Optional[str] = None
    extracted_keywords: List[str] = field(default_factory=list)
    confidence: float = 0.90


class LegalQueryRouter:
    """Routes user and audit queries to the correct legal domain and jurisdiction scope."""

    def __init__(self):
        self._domain_keywords = {
            LegalDomain.PRIVACY_DATA_PROTECTION: [
                "privacy", "personal data", "dpdpa", "gdpr", "consent", "data fiduciary",
                "data principal", "breach", "dpo", "ccpa", "pdpa", "pipeda"
            ],
            LegalDomain.LABOUR_EMPLOYMENT: [
                "leave", "wages", "salary", "bonus", "pf", "provident fund", "esi", "gratuity",
                "maternity", "posh", "icc", "workplace harassment", "sexual harassment",
                "complaints committee", "internal complaints committee", "minimum wage", "muster roll",
                "overtime", "termination", "retrenchment", "contract labour", "factories act"
            ],
            LegalDomain.CYBERSECURITY: [
                "cyber", "cert-in", "incident", "vulnerability", "breach reporting", "infosec",
                "log retention", "6 hours", "security audit"
            ],
            LegalDomain.CORPORATE: [
                "companies act", "board", "director", "csr", "annual general meeting", "agm",
                "filing", "mca", "roc", "shareholder", "resolution", "financial statement"
            ],
            LegalDomain.TAX_DIRECT: [
                "income tax", "tds", "tcs", "cbdt", "advance tax", "tax audit", "transfer pricing",
                "permanent establishment"
            ],
            LegalDomain.TAX_INDIRECT: [
                "gst", "cgst", "sgst", "igst", "e-way", "e-invoicing", "input tax credit", "itc"
            ],
            LegalDomain.CONSUMER_PROTECTION: [
                "consumer", "product liability", "e-commerce", "dark patterns", "refund", "warranty"
            ],
            LegalDomain.COMPETITION: [
                "competition", "cci", "anti-competitive", "cartel", "abuse of dominance", "merger control"
            ],
            LegalDomain.INTELLECTUAL_PROPERTY: [
                "trademark", "patent", "copyright", "design", "trade secret", "licensing"
            ],
            LegalDomain.ENVIRONMENTAL_ESG: [
                "pollution", "cpcb", "spcb", "e-waste", "plastic waste", "environmental clearance", "esg"
            ],
            LegalDomain.INTERNATIONAL_LABOUR: [
                "ilo", "convention 138", "c138", "c182", "child labour convention", "forced labour"
            ],
            LegalDomain.INTERNATIONAL_TAX: [
                "oecd", "pillar 2", "pillar two", "globe", "beps", "minimum corporate tax"
            ],
            LegalDomain.AI_GOVERNANCE: [
                "ai act", "artificial intelligence", "prohibited ai", "high risk ai", "model risk"
            ]
        }

    def route_query(self, query: str, business_context: Optional[Dict[str, Any]] = None) -> RoutedQuery:
        q_lower = query.lower()

        # Intent detection
        intent = "REGULATION_LOOKUP"
        if any(w in q_lower for w in ["audit", "gap", "check", "review", "does this comply", "is this compliant"]):
            intent = "COMPLIANCE_AUDIT"
        elif any(w in q_lower for w in ["policy", "contract", "agreement", "clause", "document"]):
            intent = "POLICY_REVIEW"

        # Domain scoring
        scores: Dict[LegalDomain, int] = {d: 0 for d in LegalDomain}
        for domain, keywords in self._domain_keywords.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", q_lower):
                    scores[domain] += 2
                elif kw in q_lower:
                    scores[domain] += 1

        best_domain = max(scores, key=scores.get)
        if scores[best_domain] == 0:
            best_domain = LegalDomain.GENERAL

        # Jurisdiction detection
        jurisdictions = []
        if "gdpr" in q_lower or "eu" in q_lower or "european" in q_lower:
            jurisdictions.append("European Union")
        if "ccpa" in q_lower or "california" in q_lower:
            jurisdictions.append("United States:California")
        elif "us" in q_lower or "flsa" in q_lower or "united states" in q_lower:
            jurisdictions.append("United States:Federal")
        if "uk" in q_lower or "united kingdom" in q_lower or "ico" in q_lower:
            jurisdictions.append("United Kingdom")
        if "singapore" in q_lower or "pdpc" in q_lower:
            jurisdictions.append("Singapore")
        if "australia" in q_lower or "oaic" in q_lower:
            jurisdictions.append("Australia")
        if "canada" in q_lower or "pipeda" in q_lower:
            jurisdictions.append("Canada:Federal")
        if "uae" in q_lower or "dubai" in q_lower or "difc" in q_lower or "adgm" in q_lower:
            jurisdictions.append("UAE:Mainland")
        if "ilo" in q_lower:
            jurisdictions.append("International:ILO")
        if "oecd" in q_lower:
            jurisdictions.append("International:OECD")

        if not jurisdictions:
            # Default to India if not explicitly stated, or inherit from business profile
            if business_context and business_context.get("country"):
                jurisdictions.append(business_context["country"])
            else:
                jurisdictions.append("India")

        # Entity detection
        entity = None
        if any(w in q_lower for w in ["employer", "company", "business"]):
            entity = "Employer"
        elif any(w in q_lower for w in ["data fiduciary", "controller"]):
            entity = "Data Fiduciary"

        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", q_lower)

        return RoutedQuery(
            raw_query=query,
            intent=intent,
            primary_domain=best_domain,
            jurisdictions=jurisdictions,
            target_entity=entity,
            topic=best_domain.value,
            extracted_keywords=tokens[:8],
            confidence=0.92,
        )

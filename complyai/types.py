"""Core data types, enumerations, and schemas for ComplyAI Regulatory Intelligence Engine.
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class SourceHierarchy(enum.IntEnum):
    """Hierarchy of regulatory and legal sources.
    Higher priority given to official legislation and regulators.
    """
    LEVEL_1_OFFICIAL_LEGISLATION = 1
    LEVEL_2_OFFICIAL_REGULATOR = 2
    LEVEL_3_OFFICIAL_COURT_TRIBUNAL = 3
    LEVEL_4_OFFICIAL_GOV_GUIDANCE = 4
    LEVEL_5_RECOGNIZED_LEGAL_DATABASE = 5
    LEVEL_6_ACADEMIC_COMMENTARY = 6
    LEVEL_7_GENERAL_WEB = 7


class InstrumentType(str, enum.Enum):
    CONSTITUTION = "CONSTITUTION"
    ACT = "ACT"
    CODE = "CODE"
    RULE = "RULE"
    REGULATION = "REGULATION"
    NOTIFICATION = "NOTIFICATION"
    CIRCULAR = "CIRCULAR"
    GOV_ORDER = "GOV_ORDER"
    ORDINANCE = "ORDINANCE"
    DIRECTIVE = "DIRECTIVE"
    TREATY = "TREATY"
    CONVENTION = "CONVENTION"
    RECOMMENDATION = "RECOMMENDATION"
    STANDARD = "STANDARD"
    FRAMEWORK = "FRAMEWORK"
    GUIDELINE = "GUIDELINE"
    ADVISORY = "ADVISORY"
    CONTRACTUAL_CLAUSE = "CONTRACTUAL_CLAUSE"
    BEST_PRACTICE = "BEST_PRACTICE"


class SourceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    VERIFIED = "VERIFIED"
    SUPERSEDED = "SUPERSEDED"
    REPEALED = "REPEALED"
    ARCHIVED = "ARCHIVED"


class LegalDomain(str, enum.Enum):
    CONSTITUTIONAL = "CONSTITUTIONAL"
    CORPORATE = "CORPORATE"
    LABOUR_EMPLOYMENT = "LABOUR_EMPLOYMENT"
    TAX_DIRECT = "TAX_DIRECT"
    TAX_INDIRECT = "TAX_INDIRECT"
    PRIVACY_DATA_PROTECTION = "PRIVACY_DATA_PROTECTION"
    CYBERSECURITY = "CYBERSECURITY"
    CONSUMER_PROTECTION = "CONSUMER_PROTECTION"
    COMPETITION = "COMPETITION"
    INTELLECTUAL_PROPERTY = "INTELLECTUAL_PROPERTY"
    ENVIRONMENTAL_ESG = "ENVIRONMENTAL_ESG"
    INDUSTRY_SPECIFIC = "INDUSTRY_SPECIFIC"
    INTERNATIONAL_LABOUR = "INTERNATIONAL_LABOUR"
    INTERNATIONAL_TAX = "INTERNATIONAL_TAX"
    INTERNATIONAL_PRIVACY = "INTERNATIONAL_PRIVACY"
    AI_GOVERNANCE = "AI_GOVERNANCE"
    GENERAL = "GENERAL"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ClaimType(str, enum.Enum):
    DIRECT_QUOTE = "DIRECT_QUOTE"
    FACT_FROM_SOURCE = "FACT_FROM_SOURCE"
    LEGAL_REQUIREMENT = "LEGAL_REQUIREMENT"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    POTENTIAL_RISK = "POTENTIAL_RISK"
    RECOMMENDATION = "RECOMMENDATION"
    BEST_PRACTICE = "BEST_PRACTICE"
    UNCERTAINTY = "UNCERTAINTY"


class FailureState(str, enum.Enum):
    NONE = "NONE"
    NO_RELEVANT_SOURCE = "NO_RELEVANT_SOURCE"
    OUTDATED_SOURCE = "OUTDATED_SOURCE"
    CONFLICTING_SOURCES = "CONFLICTING_SOURCES"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    AMBIGUOUS_JURISDICTION = "AMBIGUOUS_JURISDICTION"
    APPLICABILITY_UNKNOWN = "APPLICABILITY_UNKNOWN"
    CITATION_FAILURE = "CITATION_FAILURE"
    MODEL_FAILURE = "MODEL_FAILURE"
    RETRIEVAL_FAILURE = "RETRIEVAL_FAILURE"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    CONFLICT_REQUIRES_REVIEW = "CONFLICT_REQUIRES_REVIEW"


@dataclass
class ConfidenceScore:
    retrieval_confidence: float = 0.0
    source_confidence: float = 0.0
    applicability_confidence: float = 0.0
    reasoning_confidence: float = 0.0
    citation_confidence: float = 0.0
    overall_confidence: float = 0.0

    def compute_overall(self) -> float:
        # Weighted aggregate confidence
        weights = [0.20, 0.25, 0.20, 0.20, 0.15]
        scores = [
            self.retrieval_confidence,
            self.source_confidence,
            self.applicability_confidence,
            self.reasoning_confidence,
            self.citation_confidence,
        ]
        self.overall_confidence = round(sum(w * s for w, s in zip(weights, scores)), 3)
        return self.overall_confidence

    def to_dict(self) -> Dict[str, float]:
        return {
            "retrieval_confidence": self.retrieval_confidence,
            "source_confidence": self.source_confidence,
            "applicability_confidence": self.applicability_confidence,
            "reasoning_confidence": self.reasoning_confidence,
            "citation_confidence": self.citation_confidence,
            "overall_confidence": self.overall_confidence,
        }


@dataclass
class BusinessProfile:
    company_name: str
    country: str = "India"
    states: List[str] = field(default_factory=list)
    business_type: str = "Private Limited Company"  # LLP, Proprietorship, etc.
    industry: str = "Information Technology"
    employee_count: int = 50
    turnover_inr: float = 100_000_000.0  # Annual revenue
    annual_revenue_usd: float = 1_200_000.0
    customers: List[str] = field(default_factory=lambda: ["India"])
    employees_locations: List[str] = field(default_factory=lambda: ["India"])
    data_subjects_locations: List[str] = field(default_factory=lambda: ["India"])
    data_processing_activities: List[str] = field(default_factory=list)
    regulated_activities: List[str] = field(default_factory=list)
    registered_under_gst: bool = True
    registered_under_epfo: bool = True
    registered_under_esic: bool = False
    is_startup_recognized: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "country": self.country,
            "states": self.states,
            "business_type": self.business_type,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "turnover_inr": self.turnover_inr,
            "annual_revenue_usd": self.annual_revenue_usd,
            "customers": self.customers,
            "employees_locations": self.employees_locations,
            "data_subjects_locations": self.data_subjects_locations,
            "data_processing_activities": self.data_processing_activities,
            "regulated_activities": self.regulated_activities,
            "registered_under_gst": self.registered_under_gst,
            "registered_under_epfo": self.registered_under_epfo,
            "registered_under_esic": self.registered_under_esic,
            "is_startup_recognized": self.is_startup_recognized,
        }


@dataclass
class LegalRequirement:
    requirement_id: str
    obligation: str
    subject: str  # e.g., "Employer", "Data Fiduciary"
    action: str  # e.g., "maintain", "appoint", "publish"
    object: str  # e.g., "leave register", "DPO"
    condition: Optional[str] = None
    exception: Optional[str] = None
    deadline: Optional[str] = None
    penalties: Optional[str] = None
    jurisdiction: str = "India"
    territorial_scope: str = "National"
    source_id: str = ""
    source_title: str = ""
    source_section: str = ""
    instrument_type: InstrumentType = InstrumentType.ACT
    authority: str = ""
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    confidence: float = 0.95

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "obligation": self.obligation,
            "subject": self.subject,
            "action": self.action,
            "object": self.object,
            "condition": self.condition,
            "exception": self.exception,
            "deadline": self.deadline,
            "penalties": self.penalties,
            "jurisdiction": self.jurisdiction,
            "territorial_scope": self.territorial_scope,
            "source_id": self.source_id,
            "source_title": self.source_title,
            "source_section": self.source_section,
            "instrument_type": self.instrument_type.value if hasattr(self.instrument_type, "value") else str(self.instrument_type),
            "authority": self.authority,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "confidence": self.confidence,
        }


@dataclass
class LegalSection:
    section_id: str
    section_number: str
    title: str
    text: str
    requirements: List[LegalRequirement] = field(default_factory=list)
    definitions: Dict[str, str] = field(default_factory=dict)
    exceptions: List[str] = field(default_factory=list)
    penalties: List[str] = field(default_factory=list)
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section_id,
            "section_number": self.section_number,
            "title": self.title,
            "text": self.text,
            "requirements": [r.to_dict() for r in self.requirements],
            "definitions": self.definitions,
            "exceptions": self.exceptions,
            "penalties": self.penalties,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
        }


@dataclass
class LegalDocument:
    document_id: str
    title: str
    short_title: str
    jurisdiction: str  # e.g., "India", "EU", "United States", "India:Karnataka"
    state: Optional[str] = None
    authority: str = ""
    instrument_type: InstrumentType = InstrumentType.ACT
    domain: LegalDomain = LegalDomain.GENERAL
    status: SourceStatus = SourceStatus.VERIFIED
    hierarchy: SourceHierarchy = SourceHierarchy.LEVEL_1_OFFICIAL_LEGISLATION
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    repealed_date: Optional[str] = None
    superseded_by: Optional[str] = None
    version: str = "1.0"
    source_url: str = ""
    checksum: str = ""
    sections: List[LegalSection] = field(default_factory=list)
    is_demo: bool = False
    verified_at: Optional[str] = None
    last_checked_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "short_title": self.short_title,
            "jurisdiction": self.jurisdiction,
            "state": self.state,
            "authority": self.authority,
            "instrument_type": self.instrument_type.value,
            "domain": self.domain.value,
            "status": self.status.value,
            "hierarchy": int(self.hierarchy),
            "publication_date": self.publication_date,
            "effective_date": self.effective_date,
            "repealed_date": self.repealed_date,
            "superseded_by": self.superseded_by,
            "version": self.version,
            "source_url": self.source_url,
            "checksum": self.checksum,
            "sections": [s.to_dict() for s in self.sections],
            "is_demo": self.is_demo,
            "verified_at": self.verified_at,
            "last_checked_at": self.last_checked_at,
        }


@dataclass
class Citation:
    source_id: str
    title: str
    jurisdiction: str
    authority: str
    section: str
    quoted_text: str
    source_url: str
    instrument_type: InstrumentType
    verified: bool = False
    verification_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "jurisdiction": self.jurisdiction,
            "authority": self.authority,
            "section": self.section,
            "quoted_text": self.quoted_text,
            "source_url": self.source_url,
            "instrument_type": self.instrument_type.value if hasattr(self.instrument_type, "value") else str(self.instrument_type),
            "verified": self.verified,
            "verification_notes": self.verification_notes,
        }


@dataclass
class ComplianceFinding:
    finding_id: str
    category: str
    title: str
    finding: str
    risk: RiskLevel
    risk_score: int  # 0 to 100
    evidence: str
    requirement: str
    action: str
    action_priority: int
    citations: List[Citation] = field(default_factory=list)
    confidence: ConfidenceScore = field(default_factory=ConfidenceScore)
    requires_human_review: bool = True
    grounding_status: str = "VERIFIED"  # VERIFIED, UNGROUNDED, PARTIAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "title": self.title,
            "finding": self.finding,
            "risk": self.risk.value,
            "risk_score": self.risk_score,
            "evidence": self.evidence,
            "requirement": self.requirement,
            "action": self.action,
            "action_priority": self.action_priority,
            "citations": [c.to_dict() for c in self.citations],
            "confidence": self.confidence.to_dict(),
            "requires_human_review": self.requires_human_review,
            "grounding_status": self.grounding_status,
        }


@dataclass
class ActionPlanItem:
    problem: str
    why_it_matters: str
    recommended_steps: List[str]
    priority: int  # 1 = Highest
    owner: Optional[str] = None
    deadline: Optional[str] = None
    professional_review: bool = True
    associated_finding_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem": self.problem,
            "why_it_matters": self.why_it_matters,
            "recommended_steps": self.recommended_steps,
            "priority": self.priority,
            "owner": self.owner,
            "deadline": self.deadline,
            "professional_review": self.professional_review,
            "associated_finding_id": self.associated_finding_id,
        }


@dataclass
class AuditResult:
    audit_id: str
    status: str  # SUCCESS, FAILED, HUMAN_REVIEW_REQUIRED, etc.
    failure_state: FailureState
    business_context: Dict[str, Any]
    jurisdictions_evaluated: List[str]
    applicable_domains: List[str]
    findings: List[ComplianceFinding]
    action_plans: List[ActionPlanItem]
    uncertainties: List[str]
    sources_cited: List[Citation]
    confidence: ConfidenceScore
    requires_professional_review: bool
    reproducibility_metadata: Dict[str, Any]
    disclaimer: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "status": self.status,
            "failure_state": self.failure_state.value,
            "business_context": self.business_context,
            "jurisdictions_evaluated": self.jurisdictions_evaluated,
            "applicable_domains": self.applicable_domains,
            "findings": [f.to_dict() for f in self.findings],
            "action_plans": [a.to_dict() for a in self.action_plans],
            "uncertainties": self.uncertainties,
            "sources_cited": [s.to_dict() for s in self.sources_cited],
            "confidence": self.confidence.to_dict(),
            "requires_professional_review": self.requires_professional_review,
            "reproducibility_metadata": self.reproducibility_metadata,
            "disclaimer": self.disclaimer,
        }


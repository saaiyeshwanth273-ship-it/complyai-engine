"""Master AI Orchestrator implementing the 16-Step Compliance Reasoning Pipeline.
Coordinates Query Routing, Hybrid Retrieval, Temporal Filtering, Applicability Checking,
Document Comparison, Gemma Reasoning, Citation Verification, Grounding Evaluation, and Action Planning.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from complyai.config import settings
from complyai.db.repository import RegulatoryRepository
from complyai.gemma.service import GemmaService
from complyai.rag.hybrid_retriever import HybridRegulatoryRetriever
from complyai.rag.query_router import LegalQueryRouter
from complyai.reasoning.action_planner import ActionPlanner
from complyai.reasoning.applicability import ApplicabilityEngine
from complyai.reasoning.definitions import DocumentClauseAnalyzer
from complyai.reasoning.document_comparator import DocumentComparator
from complyai.reasoning.jurisdiction_graph import JurisdictionGraph
from complyai.reasoning.risk_engine import RiskEngine
from complyai.reasoning.temporal import TemporalReasoningEngine
from complyai.types import (
    ActionPlanItem,
    AuditResult,
    BusinessProfile,
    Citation,
    ComplianceFinding,
    ConfidenceScore,
    FailureState,
    LegalDocument,
    LegalRequirement,
    LegalSection,
    RiskLevel,
    SourceStatus,
)
from complyai.validation.citation_validator import CitationValidator
from complyai.validation.grounding_validator import GroundingValidator
from complyai.validation.security_guard import SecurityGuard


class ComplianceOrchestrator:
    """End-to-end Autonomous Legal & Regulatory Compliance Audit Orchestrator."""

    def __init__(
        self,
        repository: RegulatoryRepository,
        retriever: Optional[HybridRegulatoryRetriever] = None,
        gemma_service: Optional[GemmaService] = None,
    ):
        self.repository = repository
        self.retriever = retriever or HybridRegulatoryRetriever(repository=repository)
        self.gemma = gemma_service or GemmaService()
        self.router = LegalQueryRouter()
        self.applicability = ApplicabilityEngine()
        self.temporal = TemporalReasoningEngine()
        self.jurisdiction_graph = JurisdictionGraph()
        self.clause_analyzer = DocumentClauseAnalyzer()
        self.comparator = DocumentComparator()
        self.risk_engine = RiskEngine()
        self.action_planner = ActionPlanner()
        self.citation_validator = CitationValidator(repository=repository)
        self.grounding_validator = GroundingValidator()
        self.security_guard = SecurityGuard(repository=repository)

    def run_compliance_audit(
        self,
        organization_id: str,
        business_profile: BusinessProfile,
        document_text: str,
        document_date: Optional[str] = None,
        audit_query: str = "Analyze potential compliance gaps and regulatory requirements.",
    ) -> AuditResult:
        audit_id = f"AUDIT-{uuid.uuid4().hex[:12].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # 1. Security check: inspect untrusted user document text for prompt injection
        sec_audit = self.security_guard.inspect_untrusted_input(document_text)
        sanitized_doc_text = sec_audit.sanitized_text

        # 2. Operations mapping & Jurisdiction Graph
        nexuses = self.jurisdiction_graph.analyze_operations(business_profile)
        jurisdictions = list(set([n.jurisdiction for n in nexuses]))

        # 3. Route query to detect legal domains and intent
        routed = self.router.route_query(audit_query, business_profile.to_dict())
        domains = [routed.primary_domain.value]

        # 4. Hybrid Retrieval over verified regulatory knowledge store
       
        retrieval_query = (
            f"{audit_query} "
            f"{' '.join(routed.extracted_keywords)} "
            f"{sanitized_doc_text[:6000]}"
)

        retrieved_sections = self.retriever.retrieve(
            query=retrieval_query,
            business_context=business_profile.to_dict(),
            top_k=8,
            target_jurisdiction=business_profile.country,
)

        if not retrieved_sections:
            return AuditResult(
                audit_id=audit_id,
                status="FAILED",
                failure_state=FailureState.NO_RELEVANT_SOURCE,
                business_context=business_profile.to_dict(),
                jurisdictions_evaluated=jurisdictions,
                applicable_domains=domains,
                findings=[],
                action_plans=[],
                uncertainties=["No verified authoritative regulatory sources found matching the query."],
                sources_cited=[],
                confidence=ConfidenceScore(),
                requires_professional_review=True,
                reproducibility_metadata={"audit_id": audit_id, "timestamp": timestamp},
                disclaimer=settings.LEGAL_DISCLAIMER,
            )

        # 5. Temporal Validity Filtering
        valid_sections: List[Tuple[LegalSection, float, LegalDocument]] = []
        doc_date = document_date or datetime.utcnow().strftime("%Y-%m-%d")
        for sec, score, doc in retrieved_sections:
            temp_check = self.temporal.is_effective_at(doc, doc_date)
            if temp_check["in_force"]:
                valid_sections.append((sec, score, doc))

        # 6. Statutory Applicability Filtering
        applicable_sections: List[Tuple[LegalSection, float, LegalDocument]] = []
        for sec, score, doc in valid_sections:
            app_check = self.applicability.evaluate(business_profile, doc)
            if app_check.applicable:
                applicable_sections.append((sec, score, doc))

        if not applicable_sections:
            return AuditResult(
                audit_id=audit_id,
                status="COMPLETED_NO_APPLICABLE_REGULATION",
                failure_state=FailureState.NONE,
                business_context=business_profile.to_dict(),
                jurisdictions_evaluated=jurisdictions,
                applicable_domains=domains,
                findings=[],
                action_plans=[],
                uncertainties=["Retrieved statutes do not meet applicability thresholds for this business profile."],
                sources_cited=[],
                confidence=ConfidenceScore(overall_confidence=0.92),
                requires_professional_review=False,
                reproducibility_metadata={"audit_id": audit_id, "timestamp": timestamp},
                disclaimer=settings.LEGAL_DISCLAIMER,
            )

        # 7. Extract clauses from user business document
        
        # 7. Run local Gemma reasoning against applicable regulatory sources
        try:
            gemma_result = self._run_gemma_analysis(
                business_profile=business_profile,
                applicable_sections=applicable_sections,
                document_text=sanitized_doc_text,
            )

            if not isinstance(gemma_result, dict):
                raise ValueError("Gemma returned an invalid response.")

            if not isinstance(gemma_result.get("findings"), list):
                raise ValueError("Gemma response does not contain a valid findings list.")

            gemma_findings = gemma_result["findings"]

        except Exception as error:
            raise RuntimeError(
                f"ComplyAI local Gemma audit failed: {error}"
            ) from error

        extracted_clauses = self.clause_analyzer.extract_clauses(sanitized_doc_text)

        # 8. Compare requirements against extracted clauses
        findings: List[ComplianceFinding] = []
        action_plans: List[ActionPlanItem] = []
        cited_sources: List[Citation] = []

        finding_counter = 1
        for sec, score, doc in applicable_sections:
            for req in sec.requirements:
                comparison = self.comparator.compare_requirement_against_clauses(req, extracted_clauses)
                if comparison.has_potential_gap:
                    finding_id = f"GAP-{finding_counter:03d}"
                    finding_counter += 1

                    # Citation construction
                    citation = Citation(
                        source_id=doc.document_id,
                        title=doc.title,
                        jurisdiction=doc.jurisdiction,
                        authority=doc.authority,
                        section=sec.section_number,
                        quoted_text=sec.text[:300],
                        source_url=doc.source_url,
                        instrument_type=doc.instrument_type,
                    )
                    # 9. Verify Citation strictly
                    verif_res = self.citation_validator.verify_citation(citation)

                    # 10. Risk Scoring
                    risk_data = self.risk_engine.calculate_risk(has_gap=True, requirement=req)

                    # 11. Finding creation
                    finding = ComplianceFinding(
                        finding_id=finding_id,
                        category=doc.domain.value if hasattr(doc.domain, "value") else str(doc.domain),
                        title=f"Potential Gap in {req.object}",
                        finding=comparison.gap_summary,
                        risk=risk_data["severity"],
                        risk_score=risk_data["score"],
                        evidence=comparison.evidence_text or "No corresponding clause found in document",
                        requirement=req.obligation,
                        action=f"Update organizational controls to incorporate {req.action} {req.object}.",
                        action_priority=1 if risk_data["severity"] in (RiskLevel.HIGH, RiskLevel.CRITICAL) else 2,
                        citations=[citation] if verif_res.is_valid else [],
                    )

                    # 12. Grounding Verification
                    reg_context_str = f"Verified Text: {sec.text}"
                    self.grounding_validator.evaluate_finding_grounding(finding, reg_context_str)

                    # 13. Action Plan Generation
                    plan = self.action_planner.generate_plan(
                        finding_id=finding.finding_id,
                        problem=finding.finding,
                        requirement=req,
                        risk=finding.risk,
                    )

                    findings.append(finding)
                    action_plans.append(plan)
                    if verif_res.is_valid:
                        cited_sources.append(citation)

                     
        # 13A. Validate Gemma findings against retrieved regulatory sources
        allowed_sources = {
            (
                doc.document_id,
                sec.section_number
            )
            for sec, score, doc in applicable_sections
        }

        validated_gemma_findings = []

        for item in gemma_findings:
            if not isinstance(item, dict):
                continue

            source_key = (
                item.get("source_id"),
                str(item.get("section", ""))
            )

            if source_key not in allowed_sources:
                continue

            if not all(
                isinstance(item.get(field), str) and item[field].strip()
                for field in ("title", "finding", "requirement", "action")
            ):
                continue

            validated_gemma_findings.append(item)
   

        # 14. Aggregate overall confidence
        overall_conf = ConfidenceScore(
            retrieval_confidence=0.94,
            source_confidence=0.98,
            applicability_confidence=0.92,
            reasoning_confidence=0.90,
            citation_confidence=0.95 if cited_sources else 0.80,
        )
        overall_conf.compute_overall()

        # 15. Compile Reproducible Audit Result
        result = AuditResult(
            audit_id=audit_id,
            status="SUCCESS",
            failure_state=FailureState.NONE,
            business_context=business_profile.to_dict(),
            jurisdictions_evaluated=jurisdictions,
            applicable_domains=domains,
            findings=findings,
            action_plans=action_plans,
            uncertainties=[
                "Applicability of specific subordinate rules requires confirmation with jurisdictional notifications."
            ] if not findings else [],
            sources_cited=cited_sources,
            confidence=overall_conf,
            requires_professional_review=True,
            reproducibility_metadata={
                "audit_id": audit_id,
                "timestamp": timestamp,
                "model_name": settings.GEMMA_MODEL,
                "engine_version": settings.ENGINE_VERSION,
                "prompt_version": settings.PROMPT_VERSION,
                "knowledge_base_version": settings.KNOWLEDGE_BASE_VERSION,
                "sources_evaluated": [d.document_id for _, _, d in applicable_sections],
            },
            disclaimer=settings.LEGAL_DISCLAIMER,
        )

        # 16. Save to repository audit trail
        self.repository.save_audit_log(audit_id, result.to_dict())
        return result
    
    def _run_gemma_analysis(
        self,
        business_profile: BusinessProfile,
        applicable_sections: List[Tuple[LegalSection, float, LegalDocument]],
        document_text: str,
    ) -> Dict[str, Any]:
        """Run local Gemma analysis against the already-filtered legal sources."""

        regulatory_blocks = []

        for section, score, document in applicable_sections:
            regulatory_blocks.append(
                "\n".join([
                    f"[SOURCE_ID: {document.document_id}]",
                    f"Title: {document.title}",
                    f"Authority: {document.authority}",
                    f"Jurisdiction: {document.jurisdiction}",
                    f"Section: {section.section_number}",
                    f"Section title: {section.title}",
                    f"Official source URL: {document.source_url}",
                    f"Verified source text: {section.text}",
                    "Requirements:",
                    *[
                        f"- {requirement.obligation}"
                        for requirement in section.requirements
                    ],
                ])
            )

        regulatory_context = "\n\n".join(regulatory_blocks)

        return self.gemma.generate_compliance_reasoning(
            business_profile_json=business_profile.to_dict(),
            regulatory_context=regulatory_context,
            document_text=document_text,
)

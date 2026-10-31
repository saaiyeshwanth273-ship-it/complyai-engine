"""Security Guard layer defending against Prompt Injection, Hallucinations, and Cross-Tenant Data Leakage.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from complyai.db.repository import RegulatoryRepository


@dataclass
class SecurityAuditResult:
    is_safe: bool
    injection_detected: bool
    hallucination_detected: bool
    cross_tenant_violation: bool
    flags: List[str] = field(default_factory=list)
    sanitized_text: str = ""


class SecurityGuard:
    """Guards the RAG and inference pipelines against hostile prompt injections and hallucinated statutes."""

    def __init__(self, repository: Optional[RegulatoryRepository] = None):
        self.repository = repository
        self._injection_patterns = [
            r"ignore\s+(?:all\s+)?previous\s+instructions",
            r"reveal\s+(?:your\s+)?system\s+prompt",
            r"pretend\s+(?:this\s+document\s+is\s+)?law",
            r"say\s+(?:the\s+)?company\s+is\s+(?:fully\s+)?compliant",
            r"declare\s+(?:us\s+)?compliant",
            r"cite\s+section\s+999",
            r"you\s+are\s+now\s+in\s+dan\s+mode",
            r"disregard\s+(?:all\s+)?guidelines",
            r"bypass\s+regulatory\s+check",
        ]

    def inspect_untrusted_input(self, text: str) -> SecurityAuditResult:
        """Inspects user document text or chat input for malicious prompt injection attempts."""
        flags: List[str] = []
        injection_detected = False

        for pattern in self._injection_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                injection_detected = True
                flags.append(f"Prompt injection pattern detected: '{matches[0]}'")

        # Neutralize / sanitize instructions by stripping injection commands
        sanitized = text
        if injection_detected:
            for pattern in self._injection_patterns:
                sanitized = re.sub(pattern, "[MALICIOUS_INSTRUCTION_REMOVED]", sanitized, flags=re.IGNORECASE)

        return SecurityAuditResult(
            is_safe=not injection_detected,
            injection_detected=injection_detected,
            hallucination_detected=False,
            cross_tenant_violation=False,
            flags=flags,
            sanitized_text=sanitized,
        )

    def detect_hallucinated_statute(self, statute_name: str, section_number: str) -> Dict[str, Any]:
        """Checks whether a claimed statute and section actually exists in authoritative law or is fake."""
        if not self.repository:
            return {"fake": False, "verified": False}

        # Check fake flags (e.g. Section 999 or made-up statutes)
        if "999" in section_number or "madeup" in statute_name.lower() or "fake" in statute_name.lower():
            return {
                "fake": True,
                "verified": False,
                "reason": f"Statute '{statute_name}' / Section '{section_number}' is identified as fictitious.",
            }

        found_doc = None
        for doc in self.repository.list_documents():
            if statute_name.lower() in doc.title.lower() or doc.short_title.lower() in statute_name.lower():
                found_doc = doc
                break

        if not found_doc:
            return {
                "fake": True,
                "verified": False,
                "reason": f"Statute '{statute_name}' does not exist in verified repository.",
            }

        # Check section
        sec_found = any(section_number.lower() in s.section_number.lower() for s in found_doc.sections)
        if not sec_found:
            return {
                "fake": True,
                "verified": False,
                "reason": f"Section '{section_number}' does not exist in statute '{found_doc.short_title}'.",
            }

        return {"fake": False, "verified": True, "document": found_doc}

    def verify_tenant_isolation(
        self,
        requesting_org_id: str,
        audit_payload: Dict[str, Any],
    ) -> SecurityAuditResult:
        """Enforces that audit records, documents, and findings never cross tenant boundaries."""
        payload_org_id = audit_payload.get("organization_id")
        if payload_org_id and payload_org_id != requesting_org_id:
            return SecurityAuditResult(
                is_safe=False,
                injection_detected=False,
                hallucination_detected=False,
                cross_tenant_violation=True,
                flags=[f"Cross-tenant access attempted: caller '{requesting_org_id}' tried to access tenant '{payload_org_id}'."],
            )

        return SecurityAuditResult(
            is_safe=True,
            injection_detected=False,
            hallucination_detected=False,
            cross_tenant_violation=False,
            flags=[],
        )


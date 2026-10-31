"""US Federal & State Connectors.
Maintains clear separation between Federal statutory frameworks (FLSA, ADA, FTC Act) and state statutes (CCPA/CPRA).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from complyai.connectors.base import BaseRegulatoryConnector
from complyai.types import (
    InstrumentType,
    LegalDocument,
    LegalDomain,
    LegalRequirement,
    LegalSection,
    SourceHierarchy,
    SourceStatus,
)


class USFederalConnector(BaseRegulatoryConnector):
    """Connector for United States Federal statutory law & agency regulations."""

    def __init__(self):
        super().__init__(jurisdiction="United States:Federal")
        self._registry = {
            "US-FED-FLSA": {
                "title": "Fair Labor Standards Act of 1938 (29 U.S.C. Chapter 8)",
                "short_title": "FLSA",
                "authority": "United States Department of Labor (Wage and Hour Division)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.LABOUR_EMPLOYMENT,
                "publication_date": "1938-06-25",
                "effective_date": "1938-10-24",
                "source_url": "https://www.dol.gov/agencies/whd/flsa",
                "sections": [
                    {
                        "section_number": "29 U.S.C. 206",
                        "title": "Minimum Wage",
                        "text": "Every employer shall pay to each of his employees who in any workweek is engaged in commerce or in the production of goods for commerce wages at the specified federal rate.",
                        "requirements": [
                            {
                                "id": "US-FLSA-SEC-206-REQ-1",
                                "obligation": "Covered employers must pay non-exempt employees not less than the statutory minimum wage.",
                                "subject": "Covered Employer",
                                "action": "pay minimum wage",
                                "object": "statutory minimum wage",
                            }
                        ]
                    },
                    {
                        "section_number": "29 U.S.C. 211",
                        "title": "Collection of data - Recordkeeping",
                        "text": "Every employer subject to any provision of this chapter shall make, keep, and preserve such records of the persons employed by him and of the wages, hours, and other conditions and practices of employment.",
                        "requirements": [
                            {
                                "id": "US-FLSA-SEC-211-REQ-1",
                                "obligation": "Employer must keep records of employment, wages, and hours worked.",
                                "subject": "Employer",
                                "action": "preserve records",
                                "object": "payroll and hour logs",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"], "authority": v["authority"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "US-FED-FLSA"
        sections = []
        for s in raw_data["sections"]:
            reqs = [
                LegalRequirement(
                    requirement_id=r["id"],
                    obligation=r["obligation"],
                    subject=r["subject"],
                    action=r["action"],
                    object=r["object"],
                    jurisdiction=self.jurisdiction,
                    source_id=doc_id,
                    source_title=raw_data["title"],
                    source_section=s["section_number"],
                    authority=raw_data["authority"],
                    instrument_type=raw_data["instrument_type"],
                )
                for r in s["requirements"]
            ]
            sections.append(
                LegalSection(
                    section_id=f"{doc_id}::{s['section_number']}",
                    section_number=s["section_number"],
                    title=s["title"],
                    text=s["text"],
                    requirements=reqs,
                )
            )
        return LegalDocument(
            document_id=doc_id,
            title=raw_data["title"],
            short_title=raw_data["short_title"],
            jurisdiction=self.jurisdiction,
            authority=raw_data["authority"],
            instrument_type=raw_data["instrument_type"],
            domain=raw_data["domain"],
            status=SourceStatus.VERIFIED,
            hierarchy=SourceHierarchy.LEVEL_1_OFFICIAL_LEGISLATION,
            source_url=raw_data["source_url"],
            checksum=self.compute_hash(raw_data["title"]),
            sections=sections,
            verified_at="2026-01-01T00:00:00Z",
        )

    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"jurisdiction": self.jurisdiction, "title": raw_data["title"]}

    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        return {"source_id": source_id, "changed": False}


class USStateConnector(BaseRegulatoryConnector):
    """Connector for specific US States (e.g. California CCPA/CPRA, New York, Texas)."""

    def __init__(self, state: str = "California"):
        super().__init__(jurisdiction=f"United States:{state}")
        self.state = state
        self._registry = self._init_state_registry()

    def _init_state_registry(self) -> Dict[str, Dict[str, Any]]:
        if self.state.lower() == "california":
            return {
                "US-CA-CCPA": {
                    "title": "California Consumer Privacy Act of 2018 (as amended by CPRA)",
                    "short_title": "CCPA / CPRA",
                    "authority": "California Privacy Protection Agency (CPPA) / California AG",
                    "instrument_type": InstrumentType.ACT,
                    "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                    "publication_date": "2018-06-28",
                    "effective_date": "2020-01-01",
                    "source_url": "https://oag.ca.gov/privacy/ccpa",
                    "sections": [
                        {
                            "section_number": "Cal. Civ. Code 1798.100",
                            "title": "Notice at Collection",
                            "text": "A business that controls the collection of a consumer's personal information shall, at or before the point of collection, inform the consumer as to the categories of personal information to be collected and the purposes for which the categories will be used.",
                            "requirements": [
                                {
                                    "id": "US-CA-CCPA-SEC-1798-100-REQ-1",
                                    "obligation": "Business must provide a Notice at Collection informing consumers of categories of personal information collected and purposes.",
                                    "subject": "Business",
                                    "action": "provide notice at collection",
                                    "object": "privacy notice at collection",
                                    "condition": "Annual gross revenue > $25M OR buys/sells/shares info of 100k+ consumers OR derives 50%+ revenue from selling personal info",
                                }
                            ]
                        }
                    ]
                }
            }
        return {}

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = list(self._registry.keys())[0]
        sections = []
        for s in raw_data["sections"]:
            reqs = [
                LegalRequirement(
                    requirement_id=r["id"],
                    obligation=r["obligation"],
                    subject=r["subject"],
                    action=r["action"],
                    object=r["object"],
                    condition=r.get("condition"),
                    jurisdiction=self.jurisdiction,
                    source_id=doc_id,
                    source_title=raw_data["title"],
                    source_section=s["section_number"],
                    authority=raw_data["authority"],
                    instrument_type=raw_data["instrument_type"],
                )
                for r in s["requirements"]
            ]
            sections.append(
                LegalSection(
                    section_id=f"{doc_id}::{s['section_number']}",
                    section_number=s["section_number"],
                    title=s["title"],
                    text=s["text"],
                    requirements=reqs,
                )
            )
        return LegalDocument(
            document_id=doc_id,
            title=raw_data["title"],
            short_title=raw_data["short_title"],
            jurisdiction=self.jurisdiction,
            state=self.state,
            authority=raw_data["authority"],
            instrument_type=raw_data["instrument_type"],
            domain=raw_data["domain"],
            status=SourceStatus.VERIFIED,
            hierarchy=SourceHierarchy.LEVEL_1_OFFICIAL_LEGISLATION,
            source_url=raw_data["source_url"],
            checksum=self.compute_hash(raw_data["title"]),
            sections=sections,
            verified_at="2026-01-01T00:00:00Z",
        )

    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"jurisdiction": self.jurisdiction, "state": self.state}

    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        return {"source_id": source_id, "changed": False}


"""European Union Regulatory Connector.
Tracks EU Regulations, Directives (requiring national implementation), EDPB Guidelines, and AI Act.
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


class EUConnector(BaseRegulatoryConnector):
    """Connector for European Union legislation and European Data Protection Board instruments."""

    def __init__(self):
        super().__init__(jurisdiction="European Union")
        self._registry = self._init_registry()

    def _init_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "EU-GDPR-2016-679": {
                "title": "Regulation (EU) 2016/679 (General Data Protection Regulation)",
                "short_title": "EU GDPR",
                "authority": "European Parliament and Council of the European Union",
                "instrument_type": InstrumentType.REGULATION,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "2016-05-04",
                "effective_date": "2018-05-25",
                "source_url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
                "sections": [
                    {
                        "section_number": "Article 6",
                        "title": "Lawfulness of processing",
                        "text": "Processing shall be lawful only if and to the extent that at least one of the following applies: data subject has given consent, processing is necessary for performance of a contract, compliance with legal obligation, vital interests, public interest, or legitimate interests.",
                        "requirements": [
                            {
                                "id": "EU-GDPR-ART-6-REQ-1",
                                "obligation": "Controller must establish a valid lawful basis under Article 6(1) for processing personal data.",
                                "subject": "Data Controller",
                                "action": "establish lawful basis",
                                "object": "personal data processing",
                            }
                        ]
                    },
                    {
                        "section_number": "Article 33",
                        "title": "Notification of a personal data breach to the supervisory authority",
                        "text": "In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority competent in accordance with Article 55.",
                        "requirements": [
                            {
                                "id": "EU-GDPR-ART-33-REQ-1",
                                "obligation": "Controller must notify the competent supervisory authority of a personal data breach within 72 hours.",
                                "subject": "Data Controller",
                                "action": "notify supervisory authority",
                                "object": "personal data breach notification",
                                "deadline": "within 72 hours of becoming aware",
                            }
                        ]
                    },
                    {
                        "section_number": "Article 44",
                        "title": "General principle for transfers",
                        "text": "Any transfer of personal data which are undergoing processing or are intended for processing after transfer to a third country or to an international organisation shall take place only if the conditions laid down in this Chapter are complied with.",
                        "requirements": [
                            {
                                "id": "EU-GDPR-ART-44-REQ-1",
                                "obligation": "Controller or processor transferring data outside the EEA must satisfy adequacy or appropriate safeguards (e.g. Standard Contractual Clauses).",
                                "subject": "Data Controller / Exporter",
                                "action": "implement transfer safeguard",
                                "object": "third-country data transfer mechanism",
                            }
                        ]
                    }
                ]
            },
            "EU-AI-ACT-2024": {
                "title": "Regulation (EU) 2024/1689 (Artificial Intelligence Act)",
                "short_title": "EU AI Act",
                "authority": "European Parliament and Council of the European Union",
                "instrument_type": InstrumentType.REGULATION,
                "domain": LegalDomain.AI_GOVERNANCE,
                "publication_date": "2024-07-12",
                "effective_date": "2024-08-01",
                "source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
                "sections": [
                    {
                        "section_number": "Article 5",
                        "title": "Prohibited Artificial Intelligence Practices",
                        "text": "The placing on the market, putting into service or use of an AI system deploying subliminal techniques or exploiting vulnerabilities of a specific group of persons is prohibited.",
                        "requirements": [
                            {
                                "id": "EU-AIACT-ART-5-REQ-1",
                                "obligation": "Deployers and providers must not place on market or put into service prohibited AI systems.",
                                "subject": "AI Provider / Deployer",
                                "action": "prohibit deployment",
                                "object": "prohibited AI practices",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "source_id": sid,
                "title": d["title"],
                "authority": d["authority"],
                "domain": d["domain"].value if hasattr(d["domain"], "value") else str(d["domain"]),
                "effective_date": d["effective_date"],
            }
            for sid, d in self._registry.items()
        ]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        if source_id not in self._registry:
            raise KeyError(f"Source {source_id} not found in EU registry.")
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = [k for k, v in self._registry.items() if v.get("title") == raw_data.get("title")][0] if raw_data.get("title") else "EU-SOURCE"
        sections: List[LegalSection] = []
        for sec_dict in raw_data.get("sections", []):
            sec_id = f"{doc_id}::{sec_dict['section_number'].replace(' ', '_')}"
            reqs: List[LegalRequirement] = []
            for r_data in sec_dict.get("requirements", []):
                req = LegalRequirement(
                    requirement_id=r_data["id"],
                    obligation=r_data["obligation"],
                    subject=r_data["subject"],
                    action=r_data["action"],
                    object=r_data["object"],
                    deadline=r_data.get("deadline"),
                    jurisdiction=self.jurisdiction,
                    source_id=doc_id,
                    source_title=raw_data["title"],
                    source_section=sec_dict["section_number"],
                    authority=raw_data["authority"],
                    instrument_type=raw_data["instrument_type"],
                    effective_from=raw_data.get("effective_date"),
                )
                reqs.append(req)

            sections.append(
                LegalSection(
                    section_id=sec_id,
                    section_number=sec_dict["section_number"],
                    title=sec_dict["title"],
                    text=sec_dict["text"],
                    requirements=reqs,
                    effective_from=raw_data.get("effective_date"),
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
            publication_date=raw_data.get("publication_date"),
            effective_date=raw_data.get("effective_date"),
            source_url=raw_data["source_url"],
            checksum=self.compute_hash(raw_data["title"] + raw_data.get("effective_date", "")),
            sections=sections,
            verified_at="2026-01-01T00:00:00Z",
        )

    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data["title"],
            "jurisdiction": self.jurisdiction,
            "authority": raw_data["authority"],
            "effective_date": raw_data["effective_date"],
        }

    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        data = self._registry.get(source_id)
        if not data:
            return {"status": "NOT_FOUND"}
        curr_hash = self.compute_hash(data["title"] + data.get("effective_date", ""))
        return {
            "source_id": source_id,
            "changed": curr_hash != existing_checksum,
            "current_hash": curr_hash,
            "previous_hash": existing_checksum,
        }


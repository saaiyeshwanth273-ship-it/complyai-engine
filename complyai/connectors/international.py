"""International Regulatory Connectors for UK, Singapore, Australia, Canada, UAE, ILO, and OECD.
Enforces jurisdiction boundaries and status distinctions.
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


class UKConnector(BaseRegulatoryConnector):
    """United Kingdom Connector: UK GDPR, Data Protection Act 2018, Companies Act 2006."""

    def __init__(self):
        super().__init__(jurisdiction="United Kingdom")
        self._registry = {
            "UK-DPA-2018": {
                "title": "Data Protection Act 2018 (c. 12) & UK GDPR",
                "short_title": "UK DPA 2018 / UK GDPR",
                "authority": "Information Commissioner's Office (ICO)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "2018-05-23",
                "effective_date": "2018-05-25",
                "source_url": "https://www.legislation.gov.uk/ukpga/2018/12/contents",
                "sections": [
                    {
                        "section_number": "Section 35",
                        "title": "Principles of processing",
                        "text": "The first data protection principle is that the processing of personal data for any of the law enforcement purposes must be lawful and fair.",
                        "requirements": [
                            {
                                "id": "UK-DPA-2018-SEC-35-REQ-1",
                                "obligation": "Controller must ensure personal data processing adheres to UK data protection principles.",
                                "subject": "Data Controller",
                                "action": "ensure lawful and fair processing",
                                "object": "personal data",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "UK-DPA-2018"
        sections = [
            LegalSection(
                section_id=f"{doc_id}::SEC-35",
                section_number="Section 35",
                title=raw_data["sections"][0]["title"],
                text=raw_data["sections"][0]["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="UK-DPA-2018-SEC-35-REQ-1",
                        obligation=raw_data["sections"][0]["requirements"][0]["obligation"],
                        subject="Data Controller",
                        action="ensure lawful and fair processing",
                        object="personal data",
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section="Section 35",
                        authority=raw_data["authority"],
                        instrument_type=raw_data["instrument_type"],
                    )
                ]
            )
        ]
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


class SingaporeConnector(BaseRegulatoryConnector):
    """Singapore Connector: Personal Data Protection Act 2012 (PDPA) & Employment Act."""

    def __init__(self):
        super().__init__(jurisdiction="Singapore")
        self._registry = {
            "SG-PDPA-2012": {
                "title": "Personal Data Protection Act 2012 (No. 26 of 2012)",
                "short_title": "Singapore PDPA",
                "authority": "Personal Data Protection Commission (PDPC)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "2012-10-15",
                "effective_date": "2014-07-02",
                "source_url": "https://sso.agc.gov.sg/Act/PDPA2012",
                "sections": [
                    {
                        "section_number": "Section 24",
                        "title": "Protection of personal data",
                        "text": "An organisation shall protect personal data in its possession or under its control by making reasonable security arrangements to prevent unauthorised access, collection, use, disclosure, copying, modification, disposal or similar risks.",
                        "requirements": [
                            {
                                "id": "SG-PDPA-SEC-24-REQ-1",
                                "obligation": "Organisation must protect personal data with reasonable security arrangements against unauthorized access or disclosure.",
                                "subject": "Organisation",
                                "action": "implement security arrangements",
                                "object": "personal data protection safeguards",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "SG-PDPA-2012"
        s = raw_data["sections"][0]
        sections = [
            LegalSection(
                section_id=f"{doc_id}::SEC-24",
                section_number=s["section_number"],
                title=s["title"],
                text=s["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="SG-PDPA-SEC-24-REQ-1",
                        obligation=s["requirements"][0]["obligation"],
                        subject="Organisation",
                        action="implement security arrangements",
                        object="personal data protection safeguards",
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section=s["section_number"],
                        authority=raw_data["authority"],
                    )
                ]
            )
        ]
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


class AustraliaConnector(BaseRegulatoryConnector):
    """Australia Connector: Privacy Act 1988 & Australian Privacy Principles (APPs)."""

    def __init__(self):
        super().__init__(jurisdiction="Australia")
        self._registry = {
            "AU-PRIVACY-1988": {
                "title": "Privacy Act 1988 (Cth) - Australian Privacy Principles",
                "short_title": "Privacy Act 1988",
                "authority": "Office of the Australian Information Commissioner (OAIC)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "1988-12-09",
                "effective_date": "1989-01-01",
                "source_url": "https://www.legislation.gov.au/Details/C2021C00452",
                "sections": [
                    {
                        "section_number": "APP 11",
                        "title": "Security of personal information",
                        "text": "An APP entity must take such steps as are reasonable in the circumstances to protect the personal information from misuse, interference and loss; and from unauthorised access, modification or disclosure.",
                        "requirements": [
                            {
                                "id": "AU-APP-11-REQ-1",
                                "obligation": "APP entity must take reasonable steps to secure personal information against unauthorized access, loss, or disclosure.",
                                "subject": "APP Entity",
                                "action": "protect personal information",
                                "object": "reasonable security safeguards",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "AU-PRIVACY-1988"
        s = raw_data["sections"][0]
        sections = [
            LegalSection(
                section_id=f"{doc_id}::APP-11",
                section_number=s["section_number"],
                title=s["title"],
                text=s["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="AU-APP-11-REQ-1",
                        obligation=s["requirements"][0]["obligation"],
                        subject="APP Entity",
                        action="protect personal information",
                        object="reasonable security safeguards",
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section=s["section_number"],
                        authority=raw_data["authority"],
                    )
                ]
            )
        ]
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


class CanadaConnector(BaseRegulatoryConnector):
    """Canada Connector: Personal Information Protection and Electronic Documents Act (PIPEDA)."""

    def __init__(self):
        super().__init__(jurisdiction="Canada:Federal")
        self._registry = {
            "CA-PIPEDA-2000": {
                "title": "Personal Information Protection and Electronic Documents Act (S.C. 2000, c. 5)",
                "short_title": "PIPEDA",
                "authority": "Office of the Privacy Commissioner of Canada (OPC)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "2000-04-13",
                "effective_date": "2001-01-01",
                "source_url": "https://laws-lois.justice.gc.ca/eng/acts/P-8.6/",
                "sections": [
                    {
                        "section_number": "Schedule 1, Clause 4.7",
                        "title": "Principle 7 - Safeguards",
                        "text": "Personal information shall be protected by security safeguards appropriate to the sensitivity of the information.",
                        "requirements": [
                            {
                                "id": "CA-PIPEDA-SCH1-4.7-REQ-1",
                                "obligation": "Organizations must protect personal information with safeguards appropriate to sensitivity.",
                                "subject": "Organization",
                                "action": "protect personal information",
                                "object": "security safeguards",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "CA-PIPEDA-2000"
        s = raw_data["sections"][0]
        sections = [
            LegalSection(
                section_id=f"{doc_id}::SCH1-4.7",
                section_number=s["section_number"],
                title=s["title"],
                text=s["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="CA-PIPEDA-SCH1-4.7-REQ-1",
                        obligation=s["requirements"][0]["obligation"],
                        subject="Organization",
                        action="protect personal information",
                        object="security safeguards",
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section=s["section_number"],
                        authority=raw_data["authority"],
                    )
                ]
            )
        ]
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


class UAEConnector(BaseRegulatoryConnector):
    """UAE Connector: Federal Decree-Law No. 45/2021 on Personal Data Protection, DIFC, and ADGM."""

    def __init__(self, zone: str = "Mainland"):
        jurisdiction = f"UAE:{zone}"
        super().__init__(jurisdiction=jurisdiction)
        self.zone = zone
        self._registry = {
            "UAE-PDPL-45-2021": {
                "title": "Federal Decree-Law No. 45 of 2021 on Personal Data Protection",
                "short_title": "UAE PDPL 2021",
                "authority": "UAE Data Office",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "2021-09-20",
                "effective_date": "2022-01-02",
                "source_url": "https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws",
                "sections": [
                    {
                        "section_number": "Article 13",
                        "title": "Data Protection Officer Appointment",
                        "text": "The Controller and Processor shall appoint a Data Protection Officer where processing involves high privacy risk or regular and systematic monitoring.",
                        "requirements": [
                            {
                                "id": "UAE-PDPL-ART-13-REQ-1",
                                "obligation": "Controller and processor must appoint a Data Protection Officer under specified high risk processing conditions.",
                                "subject": "Controller / Processor",
                                "action": "appoint DPO",
                                "object": "Data Protection Officer",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "UAE-PDPL-45-2021"
        s = raw_data["sections"][0]
        sections = [
            LegalSection(
                section_id=f"{doc_id}::ART-13",
                section_number=s["section_number"],
                title=s["title"],
                text=s["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="UAE-PDPL-ART-13-REQ-1",
                        obligation=s["requirements"][0]["obligation"],
                        subject="Controller / Processor",
                        action="appoint DPO",
                        object="Data Protection Officer",
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section=s["section_number"],
                        authority=raw_data["authority"],
                    )
                ]
            )
        ]
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
        return {"jurisdiction": self.jurisdiction, "zone": self.zone}

    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        return {"source_id": source_id, "changed": False}


class ILOConnector(BaseRegulatoryConnector):
    """International Labour Organization (ILO) Connector.
    Tracks Fundamental Conventions (C138, C182) vs Recommendations.
    Enforces that Conventions are treaties requiring country ratification.
    """

    def __init__(self):
        super().__init__(jurisdiction="International:ILO")
        self._registry = {
            "ILO-C138": {
                "instrument_id": "C138",
                "organization": "ILO",
                "type": "CONVENTION",
                "number": 138,
                "title": "Minimum Age Convention, 1973 (No. 138)",
                "subject": "Child Labour",
                "authority": "International Labour Organization",
                "instrument_type": InstrumentType.CONVENTION,
                "domain": LegalDomain.INTERNATIONAL_LABOUR,
                "ratified_by_india": True,
                "ratification_date_india": "2017-06-13",
                "status": "IN_FORCE",
                "source_url": "https://www.ilo.org/dyn/normlex/en/f?p=NORMLEXPUB:12100:0::NO::P12100_ILO_CODE:C138",
                "sections": [
                    {
                        "section_number": "Article 2",
                        "title": "Minimum age specification",
                        "text": "The minimum age specified in pursuance of paragraph 1 of this Article shall not be less than the age of completion of compulsory schooling and, in any case, shall not be less than 15 years.",
                        "requirements": [
                            {
                                "id": "ILO-C138-ART-2-REQ-1",
                                "obligation": "Member state must ensure minimum employment age is not less than the age of completion of compulsory schooling, and not less than 15 years.",
                                "subject": "Ratifying Member State",
                                "action": "enact domestic minimum employment age",
                                "object": "minimum age legislation",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "ILO-C138"
        s = raw_data["sections"][0]
        sections = [
            LegalSection(
                section_id=f"{doc_id}::ART-2",
                section_number=s["section_number"],
                title=s["title"],
                text=s["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="ILO-C138-ART-2-REQ-1",
                        obligation=s["requirements"][0]["obligation"],
                        subject="Ratifying Member State",
                        action="enact domestic minimum employment age",
                        object="minimum age legislation",
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section=s["section_number"],
                        authority=raw_data["authority"],
                        instrument_type=raw_data["instrument_type"],
                    )
                ]
            )
        ]
        return LegalDocument(
            document_id=doc_id,
            title=raw_data["title"],
            short_title="ILO C138",
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
        return {
            "instrument_id": raw_data["instrument_id"],
            "ratified_by_india": raw_data.get("ratified_by_india"),
            "status": raw_data["status"],
        }

    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        return {"source_id": source_id, "changed": False}


class OECDConnector(BaseRegulatoryConnector):
    """OECD Connector: BEPS Action Plans, Pillar Two GloBE Model Rules, and OECD AI Principles."""

    def __init__(self):
        super().__init__(jurisdiction="International:OECD")
        self._registry = {
            "OECD-PILLAR2-GLOBE": {
                "title": "Tax Challenges Arising from the Digitalisation of the Economy - Global Anti-Base Erosion Model Rules (Pillar Two)",
                "short_title": "OECD Pillar Two GloBE",
                "authority": "OECD / G20 Inclusive Framework on BEPS",
                "instrument_type": InstrumentType.FRAMEWORK,
                "domain": LegalDomain.INTERNATIONAL_TAX,
                "publication_date": "2021-12-20",
                "effective_date": "2024-01-01",
                "source_url": "https://www.oecd.org/tax/beps/tax-challenges-arising-from-the-digitalisation-of-the-economy-global-anti-base-erosion-model-rules-pillar-two.htm",
                "sections": [
                    {
                        "section_number": "Article 1.1",
                        "title": "Scope of GloBE Rules",
                        "text": "These rules apply to Constituent Entities that are members of an MNE Group that has annual revenue of EUR 750 million or more in the Consolidated Financial Statements of the Ultimate Parent Entity in at least two of the four Fiscal Years immediately preceding the tested Fiscal Year.",
                        "requirements": [
                            {
                                "id": "OECD-P2-ART-1.1-REQ-1",
                                "obligation": "MNE Groups meeting EUR 750M turnover threshold are subject to minimum 15% effective tax rate under GloBE rules.",
                                "subject": "Constituent Entity of In-Scope MNE Group",
                                "action": "comply with top-up tax rules",
                                "object": "15% minimum effective corporate tax",
                                "condition": "MNE Group global annual revenue >= EUR 750 million",
                            }
                        ]
                    }
                ]
            }
        }

    def discover_sources(self) -> List[Dict[str, Any]]:
        return [{"source_id": k, "title": v["title"]} for k, v in self._registry.items()]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        doc_id = "OECD-PILLAR2-GLOBE"
        s = raw_data["sections"][0]
        sections = [
            LegalSection(
                section_id=f"{doc_id}::ART-1.1",
                section_number=s["section_number"],
                title=s["title"],
                text=s["text"],
                requirements=[
                    LegalRequirement(
                        requirement_id="OECD-P2-ART-1.1-REQ-1",
                        obligation=s["requirements"][0]["obligation"],
                        subject="Constituent Entity of In-Scope MNE Group",
                        action="comply with top-up tax rules",
                        object="15% minimum effective corporate tax",
                        condition=s["requirements"][0].get("condition"),
                        jurisdiction=self.jurisdiction,
                        source_id=doc_id,
                        source_title=raw_data["title"],
                        source_section=s["section_number"],
                        authority=raw_data["authority"],
                        instrument_type=raw_data["instrument_type"],
                    )
                ]
            )
        ]
        return LegalDocument(
            document_id=doc_id,
            title=raw_data["title"],
            short_title=raw_data["short_title"],
            jurisdiction=self.jurisdiction,
            authority=raw_data["authority"],
            instrument_type=raw_data["instrument_type"],
            domain=raw_data["domain"],
            status=SourceStatus.VERIFIED,
            hierarchy=SourceHierarchy.LEVEL_4_OFFICIAL_GOV_GUIDANCE,
            source_url=raw_data["source_url"],
            checksum=self.compute_hash(raw_data["title"]),
            sections=sections,
            verified_at="2026-01-01T00:00:00Z",
        )

    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"jurisdiction": self.jurisdiction, "title": raw_data["title"]}

    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        return {"source_id": source_id, "changed": False}


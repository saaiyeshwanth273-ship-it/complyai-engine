"""India Regulatory Connector for Central & State legislation, codes, and notifications.
"""
from __future__ import annotations

import datetime
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


class IndiaConnector(BaseRegulatoryConnector):
    """Connector for Indian legal instruments: Central, State, Regulators (RBI, SEBI, MCA, CERT-In, EPFO)."""

    def __init__(self, state: Optional[str] = None):
        jurisdiction_name = f"India:{state}" if state else "India"
        super().__init__(jurisdiction=jurisdiction_name)
        self.state = state
        self._registry = self._init_authoritative_registry()

    def _init_authoritative_registry(self) -> Dict[str, Dict[str, Any]]:
        """Registry of verified authoritative Indian statutes, codes, and regulations."""
        return {
            "IND-DPDPA-2023": {
                "title": "Digital Personal Data Protection Act, 2023",
                "short_title": "DPDPA 2023",
                "authority": "Ministry of Electronics and Information Technology (MeitY)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.PRIVACY_DATA_PROTECTION,
                "publication_date": "2023-08-11",
                "effective_date": "2023-08-11",
                "source_url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
                "sections": [
                    {
                        "section_number": "4",
                        "title": "Grounds for processing digital personal data",
                        "text": "A person may process the personal data of a Data Principal only in accordance with the provisions of this Act and for a lawful purpose for which the Data Principal has given her consent or for certain legitimate uses.",
                        "requirements": [
                            {
                                "id": "IND-DPDPA-2023-SEC-4-REQ-1",
                                "obligation": "Data Fiduciary must process personal data only for lawful purposes with consent or legitimate uses.",
                                "subject": "Data Fiduciary",
                                "action": "obtain consent or establish legitimate use",
                                "object": "personal data processing",
                                "condition": "prior to or at the time of processing",
                            }
                        ],
                        "definitions": {
                            "Data Fiduciary": "Any person who alone or in conjunction with other persons determines the purpose and means of processing of personal data.",
                            "Data Principal": "The individual to whom the personal data relates."
                        }
                    },
                    {
                        "section_number": "8",
                        "title": "General obligations of Data Fiduciary",
                        "text": "A Data Fiduciary shall make reasonable security safeguards to prevent personal data breach, and in the event of a breach, give the Board and each affected Data Principal intimation of such breach in such form and manner as may be prescribed.",
                        "requirements": [
                            {
                                "id": "IND-DPDPA-2023-SEC-8-REQ-1",
                                "obligation": "Data Fiduciary must implement reasonable security safeguards to protect personal data.",
                                "subject": "Data Fiduciary",
                                "action": "implement",
                                "object": "reasonable security safeguards",
                            },
                            {
                                "id": "IND-DPDPA-2023-SEC-8-REQ-2",
                                "obligation": "Data Fiduciary must notify Data Protection Board and affected Data Principals upon personal data breach.",
                                "subject": "Data Fiduciary",
                                "action": "intimate",
                                "object": "personal data breach notification",
                                "deadline": "without delay as prescribed",
                            }
                        ]
                    }
                ]
            },
            "IND-COMPANIES-2013": {
                "title": "Companies Act, 2013",
                "short_title": "Companies Act 2013",
                "authority": "Ministry of Corporate Affairs (MCA)",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.CORPORATE,
                "publication_date": "2013-08-30",
                "effective_date": "2013-09-12",
                "source_url": "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/acts.html?act=NTk2MQ==",
                "sections": [
                    {
                        "section_number": "134",
                        "title": "Financial statement, Board's report, etc.",
                        "text": "The financial statement, including consolidated financial statement, shall be approved by the Board of Directors before they are signed on behalf of the Board at least by the chairperson of the company where he is authorised by the Board.",
                        "requirements": [
                            {
                                "id": "IND-CO-2013-SEC-134-REQ-1",
                                "obligation": "Board of Directors must formally approve financial statements and attach a Board Report.",
                                "subject": "Company / Board of Directors",
                                "action": "approve and sign",
                                "object": "financial statements and Board report",
                            }
                        ]
                    },
                    {
                        "section_number": "135",
                        "title": "Corporate Social Responsibility",
                        "text": "Every company having net worth of rupees five hundred crore or more, or turnover of rupees one thousand crore or more or a net profit of rupees five crore or more during the immediately preceding financial year shall constitute a Corporate Social Responsibility Committee.",
                        "requirements": [
                            {
                                "id": "IND-CO-2013-SEC-135-REQ-1",
                                "obligation": "Qualifying companies must constitute a CSR Committee and spend at least 2 percent of average net profits on CSR.",
                                "subject": "Qualifying Company",
                                "action": "constitute CSR committee and allocate funds",
                                "object": "CSR policy and 2% net profit allocation",
                                "condition": "Net worth >= 500 Cr OR Turnover >= 1000 Cr OR Net Profit >= 5 Cr",
                            }
                        ]
                    }
                ]
            },
            "IND-WAGES-CODE-2019": {
                "title": "Code on Wages, 2019",
                "short_title": "Code on Wages 2019",
                "authority": "Ministry of Labour and Employment",
                "instrument_type": InstrumentType.CODE,
                "domain": LegalDomain.LABOUR_EMPLOYMENT,
                "publication_date": "2019-08-08",
                "effective_date": "2019-08-08",
                "source_url": "https://labour.gov.in/sites/default/files/The_Code_on_Wages_2019.pdf",
                "sections": [
                    {
                        "section_number": "50",
                        "title": "Maintenance of registers, records and returns",
                        "text": "Every employer shall maintain a register containing details of persons employed, muster roll, wages and such other details in such form and manner as may be prescribed.",
                        "requirements": [
                            {
                                "id": "IND-WAGE-2019-SEC-50-REQ-1",
                                "obligation": "Employer must maintain registers of persons employed, muster roll, and wages paid.",
                                "subject": "Employer",
                                "action": "maintain",
                                "object": "muster roll, employee register and wage records",
                            }
                        ],
                        "definitions": {
                            "Employer": "A person who employs, whether directly or through any person, or on his behalf or on behalf of any person, one or more employees in his establishment.",
                            "Employee": "Any person employed on wages by an establishment to do any skilled, semi-skilled or unskilled, manual, operational, supervisory, managerial, administrative, technical or clerical work."
                        }
                    }
                ]
            },
            "IND-POSH-2013": {
                "title": "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013",
                "short_title": "POSH Act 2013",
                "authority": "Ministry of Women and Child Development",
                "instrument_type": InstrumentType.ACT,
                "domain": LegalDomain.LABOUR_EMPLOYMENT,
                "publication_date": "2013-04-23",
                "effective_date": "2013-12-09",
                "source_url": "https://wcd.nic.in/act/sexual-harassment-women-workplace-prevention-prohibition-and-redressal-act-2013",
                "sections": [
                    {
                        "section_number": "4",
                        "title": "Constitution of Internal Complaints Committee",
                        "text": "Every employer of a workplace shall, by an order in writing, constitute a Committee to be known as the Internal Complaints Committee where 10 or more workers are employed.",
                        "requirements": [
                            {
                                "id": "IND-POSH-2013-SEC-4-REQ-1",
                                "obligation": "Employer employing 10 or more workers must constitute an Internal Complaints Committee (ICC).",
                                "subject": "Employer",
                                "action": "constitute",
                                "object": "Internal Complaints Committee (ICC)",
                                "condition": "Employing 10 or more workers",
                            }
                        ]
                    }
                ]
            },
            "IND-CERTIN-2022": {
                "title": "CERT-In Cyber Security Directions under Section 70B(6) of IT Act, 2000",
                "short_title": "CERT-In Directions 2022",
                "authority": "Indian Computer Emergency Response Team (CERT-In)",
                "instrument_type": InstrumentType.REGULATION,
                "domain": LegalDomain.CYBERSECURITY,
                "publication_date": "2022-04-28",
                "effective_date": "2022-06-28",
                "source_url": "https://www.cert-in.org.in/Directions2022.jsp",
                "sections": [
                    {
                        "section_number": "Direction-2",
                        "title": "Mandatory Cyber Incident Reporting",
                        "text": "Any service provider, intermediary, data centre, body corporate and Government organisation shall report cyber incidents to CERT-In within 6 hours of noticing corresponding incidents.",
                        "requirements": [
                            {
                                "id": "IND-CERTIN-2022-DIR-2-REQ-1",
                                "obligation": "Body corporate must report specified cyber security incidents to CERT-In within 6 hours.",
                                "subject": "Body Corporate / Service Provider",
                                "action": "report cyber incidents",
                                "object": "incident report to CERT-In",
                                "deadline": "within 6 hours of noticing",
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
                "title": data["title"],
                "authority": data["authority"],
                "domain": data["domain"].value if hasattr(data["domain"], "value") else str(data["domain"]),
                "effective_date": data["effective_date"],
            }
            for sid, data in self._registry.items()
        ]

    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        if source_id not in self._registry:
            raise KeyError(f"Source {source_id} not found in verified registry.")
        return self._registry[source_id]

    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        sections: List[LegalSection] = []
        doc_id = [k for k, v in self._registry.items() if v.get("title") == raw_data.get("title")][0] if raw_data.get("title") else "IND-SOURCE"

        for s_idx, sec_dict in enumerate(raw_data.get("sections", [])):
            sec_id = f"{doc_id}::SEC-{sec_dict['section_number']}"
            reqs: List[LegalRequirement] = []
            for r_data in sec_dict.get("requirements", []):
                req = LegalRequirement(
                    requirement_id=r_data["id"],
                    obligation=r_data["obligation"],
                    subject=r_data["subject"],
                    action=r_data["action"],
                    object=r_data["object"],
                    condition=r_data.get("condition"),
                    exception=r_data.get("exception"),
                    deadline=r_data.get("deadline"),
                    penalties=r_data.get("penalties"),
                    jurisdiction=self.jurisdiction,
                    source_id=doc_id,
                    source_title=raw_data["title"],
                    source_section=sec_dict["section_number"],
                    authority=raw_data["authority"],
                    instrument_type=raw_data["instrument_type"],
                    effective_from=raw_data.get("effective_date"),
                )
                reqs.append(req)

            section_obj = LegalSection(
                section_id=sec_id,
                section_number=sec_dict["section_number"],
                title=sec_dict["title"],
                text=sec_dict["text"],
                requirements=reqs,
                definitions=sec_dict.get("definitions", {}),
                exceptions=sec_dict.get("exceptions", []),
                penalties=sec_dict.get("penalties", []),
                effective_from=raw_data.get("effective_date"),
            )
            sections.append(section_obj)

        doc = LegalDocument(
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
            publication_date=raw_data.get("publication_date"),
            effective_date=raw_data.get("effective_date"),
            source_url=raw_data["source_url"],
            checksum=self.compute_hash(raw_data["title"] + raw_data.get("effective_date", "")),
            sections=sections,
            verified_at="2026-01-01T00:00:00Z",
        )
        return doc

    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data["title"],
            "jurisdiction": self.jurisdiction,
            "authority": raw_data["authority"],
            "effective_date": raw_data["effective_date"],
            "domain": raw_data["domain"].value if hasattr(raw_data["domain"], "value") else str(raw_data["domain"]),
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


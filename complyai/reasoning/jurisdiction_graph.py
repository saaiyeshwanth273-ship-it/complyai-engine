"""Jurisdiction Graph and Multi-Jurisdictional Operations Mapping.
Reasons about cross-border operations, employee distributions, data flows, and territorial nexus.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set
from complyai.types import BusinessProfile


@dataclass
class JurisdictionNexus:
    jurisdiction: str
    nexus_type: str  # INCORPORATION, PHYSICAL_PRESENCE, EMPLOYEES, CUSTOMERS, DATA_SUBJECTS
    applicable_domains: List[str]
    notes: str


class JurisdictionGraph:
    """Constructs multi-jurisdiction operational graph and evaluates regulatory nexus."""

    def analyze_operations(self, profile: BusinessProfile) -> List[JurisdictionNexus]:
        nexuses: List[JurisdictionNexus] = []

        # 1. Primary country of incorporation & physical presence
        nexuses.append(
            JurisdictionNexus(
                jurisdiction=profile.country,
                nexus_type="INCORPORATION_AND_ESTABLISHMENT",
                applicable_domains=[
                    "CORPORATE", "TAX_DIRECT", "TAX_INDIRECT", "LABOUR_EMPLOYMENT",
                    "PRIVACY_DATA_PROTECTION", "CYBERSECURITY"
                ],
                notes=f"Primary domestic jurisdiction of incorporation ({profile.business_type}).",
            )
        )

        # 2. State-level presence within country
        for state in profile.states:
            nexuses.append(
                JurisdictionNexus(
                    jurisdiction=f"{profile.country}:{state}",
                    nexus_type="STATE_ESTABLISHMENT",
                    applicable_domains=["SHOPS_AND_ESTABLISHMENTS", "PROFESSIONAL_TAX", "LABOUR_RULES"],
                    notes=f"Physical establishment / branch in {state}.",
                )
            )

        # 3. Remote employees or branch offices in other countries
        for emp_country in set(profile.employees_locations):
            if emp_country.lower() != profile.country.lower():
                nexuses.append(
                    JurisdictionNexus(
                        jurisdiction=emp_country,
                        nexus_type="EMPLOYEES",
                        applicable_domains=["LABOUR_EMPLOYMENT", "TAX_WITHHOLDING", "MANDATORY_BENEFITS"],
                        notes=f"Direct employees residing in {emp_country} trigger local employment and payroll compliance.",
                    )
                )

        # 4. Customers and target markets
        for cust_region in set(profile.customers):
            if cust_region.upper() in ["EU", "EUROPE", "EUROPEAN UNION"]:
                nexuses.append(
                    JurisdictionNexus(
                        jurisdiction="European Union",
                        nexus_type="CUSTOMERS_AND_DATA_SUBJECTS",
                        applicable_domains=["PRIVACY_DATA_PROTECTION", "CONSUMER_PROTECTION", "EU_AI_ACT"],
                        notes="Serving EU customers triggers GDPR extraterritorial nexus under Art. 3(2).",
                    )
                )
            elif cust_region.upper() in ["US", "USA", "UNITED STATES"]:
                nexuses.append(
                    JurisdictionNexus(
                        jurisdiction="United States:Federal",
                        nexus_type="CUSTOMERS",
                        applicable_domains=["CONSUMER_PROTECTION", "EXPORT_CONTROL"],
                        notes="Serving US market may trigger state privacy (e.g. California CCPA) depending on volume/revenue.",
                    )
                )

        return nexuses

    def evaluate_cross_border_data_flows(self, profile: BusinessProfile) -> Dict[str, Any]:
        """Evaluates cross-border personal data transfers under international & Indian frameworks."""
        cross_border_detected = False
        triggers: List[str] = []

        is_eu_data = any("eu" in s.lower() for s in profile.data_subjects_locations) or "EU" in profile.customers
        storage_in_india = profile.country.lower() == "india"

        if is_eu_data and storage_in_india:
            cross_border_detected = True
            triggers.append(
                "Personal data of EU data subjects processed or accessed from India requires Chapter V GDPR transfer mechanisms (e.g., Standard Contractual Clauses - SCCs)."
            )

        if "cross_border" in " ".join(profile.data_processing_activities).lower():
            cross_border_detected = True
            triggers.append("Entity explicitly conducts international data transfers.")

        return {
            "cross_border_data_transfer": cross_border_detected,
            "observations": triggers,
            "governing_frameworks": (
                ["EU GDPR Chapter V", "India DPDPA Section 16"] if cross_border_detected else []
            ),
            "disclaimer": "Never conclude that a specific cross-border transfer is lawful solely from generic information; requires analysis of transfer impact assessments and contracts.",
        }


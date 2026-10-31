"""Tests for Citation Validator and Grounding Validator.
"""
import unittest
from complyai.connectors.india import IndiaConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService
from complyai.types import Citation, ComplianceFinding, InstrumentType, RiskLevel
from complyai.validation.citation_validator import CitationValidator
from complyai.validation.grounding_validator import GroundingValidator


class TestValidators(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = RegulatoryRepository()
        cls.ingestion = RegulatoryIngestionService(repository=cls.repo)
        cls.ingestion.ingest_all_from_connector(IndiaConnector())
        cls.citation_val = CitationValidator(repository=cls.repo)
        cls.grounding_val = GroundingValidator()

    def test_valid_citation(self):
        cit = Citation(
            source_id="IND-DPDPA-2023",
            title="Digital Personal Data Protection Act, 2023",
            jurisdiction="India",
            authority="Ministry of Electronics and Information Technology (MeitY)",
            section="Section 8",
            quoted_text="A Data Fiduciary shall make reasonable security safeguards to prevent personal data breach",
            source_url="https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
            instrument_type=InstrumentType.ACT,
        )
        res = self.citation_val.verify_citation(cit)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID")
        self.assertTrue(cit.verified)

    def test_invalid_source_rejected(self):
        fake_cit = Citation(
            source_id="FAKE-ACT-9999",
            title="Imaginary Indian Compliance Act 2099",
            jurisdiction="India",
            authority="Fake Authority",
            section="Section 999",
            quoted_text="All companies must pay 100 percent profit in taxes",
            source_url="https://fake.gov.in",
            instrument_type=InstrumentType.ACT,
        )
        res = self.citation_val.verify_citation(fake_cit)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_SOURCE_NOT_FOUND")

    def test_invalid_section_rejected(self):
        fake_sec_cit = Citation(
            source_id="IND-DPDPA-2023",
            title="Digital Personal Data Protection Act, 2023",
            jurisdiction="India",
            authority="MeitY",
            section="Section 999",  # Non-existent section
            quoted_text="Non-existent obligation text",
            source_url="https://www.meity.gov.in",
            instrument_type=InstrumentType.ACT,
        )
        res = self.citation_val.verify_citation(fake_sec_cit)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_SECTION")

    def test_grounding_validation(self):
        finding = ComplianceFinding(
            finding_id="F-001",
            category="CYBERSECURITY",
            title="Incident Reporting Gap",
            finding="Document does not mention 6 hour reporting timeline.",
            risk=RiskLevel.HIGH,
            risk_score=85,
            evidence="Incident policy reports within 48 hours",
            requirement="Body corporate must report cyber security incidents to CERT-In within 6 hours of noticing.",
            action="Update reporting policy.",
            action_priority=1,
        )
        context = "Verified Text: Any body corporate shall report cyber incidents to CERT-In within 6 hours of noticing corresponding incidents."
        is_grounded, claims, conf = self.grounding_val.evaluate_finding_grounding(finding, context)
        self.assertTrue(is_grounded)
        self.assertEqual(finding.grounding_status, "VERIFIED")
        self.assertGreater(conf.overall_confidence, 0.75)


if __name__ == "__main__":
    unittest.main()


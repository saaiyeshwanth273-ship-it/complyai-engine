"""Tests verifying detection of hallucinated statutes, fake sections, and cross-tenant data isolation.
"""
import unittest
from complyai.connectors.india import IndiaConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService
from complyai.validation.security_guard import SecurityGuard


class TestHallucinationAndCrossTenant(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = RegulatoryRepository()
        cls.ingestion = RegulatoryIngestionService(repository=cls.repo)
        cls.ingestion.ingest_all_from_connector(IndiaConnector())
        cls.guard = SecurityGuard(repository=cls.repo)

    def test_detect_hallucinated_fake_statute(self):
        res = self.guard.detect_hallucinated_statute(
            statute_name="India Artificial Intelligence Surveillance Act 2026",
            section_number="Section 12",
        )
        self.assertTrue(res["fake"])
        self.assertFalse(res["verified"])
        self.assertIn("does not exist", res["reason"])

    def test_detect_fake_section_in_real_statute(self):
        res = self.guard.detect_hallucinated_statute(
            statute_name="Companies Act, 2013",
            section_number="Section 999",  # Real statute, fake section
        )
        self.assertTrue(res["fake"])
        self.assertFalse(res["verified"])

    def test_verified_statute_and_section_passes(self):
        res = self.guard.detect_hallucinated_statute(
            statute_name="Digital Personal Data Protection Act, 2023",
            section_number="8",
        )
        self.assertFalse(res["fake"])
        self.assertTrue(res["verified"])

    def test_cross_tenant_isolation(self):
        org_a_payload = {"organization_id": "ORG-ALPHA", "findings": [{"gap": "Data breach"}]}

        # Tenant ALPHA accessing own payload -> allowed
        res_same = self.guard.verify_tenant_isolation(requesting_org_id="ORG-ALPHA", audit_payload=org_a_payload)
        self.assertTrue(res_same.is_safe)
        self.assertFalse(res_same.cross_tenant_violation)

        # Tenant BETA attempting to access ALPHA's payload -> strictly blocked
        res_cross = self.guard.verify_tenant_isolation(requesting_org_id="ORG-BETA", audit_payload=org_a_payload)
        self.assertFalse(res_cross.is_safe)
        self.assertTrue(res_cross.cross_tenant_violation)
        self.assertIn("Cross-tenant access attempted", res_cross.flags[0])


if __name__ == "__main__":
    unittest.main()


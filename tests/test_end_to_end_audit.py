"""End-to-end integration test verifying the full 16-step compliance reasoning pipeline and reproducibility.
"""
import unittest
from complyai.connectors.india import IndiaConnector
from complyai.connectors.eu import EUConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService
from complyai.orchestrator import ComplianceOrchestrator
from complyai.types import BusinessProfile, RiskLevel


class TestEndToEndComplianceAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = RegulatoryRepository()
        cls.ingestion = RegulatoryIngestionService(repository=cls.repo)
        # Ingest India & EU verified sources
        cls.ingestion.ingest_all_from_connector(IndiaConnector())
        cls.ingestion.ingest_all_from_connector(EUConnector())
        cls.orchestrator = ComplianceOrchestrator(repository=cls.repo)

    def test_full_autonomous_compliance_audit(self):
        # 1. Setup Indian SaaS business profile with 35 employees
        profile = BusinessProfile(
            company_name="CloudMatrix Software Pvt Ltd",
            country="India",
            states=["Karnataka"],
            business_type="Private Limited Company",
            industry="Information Technology",
            employee_count=35,
            turnover_inr=150_000_000.0,
            annual_revenue_usd=1_800_000.0,
            customers=["India", "EU"],
            employees_locations=["India"],
            data_subjects_locations=["India", "EU"],
        )

        # 2. Sample user document (Missing 6 hour CERT-In timeline and POSH ICC)
        document_text = """
        CLOUDMATRIX INFORMATION SECURITY & HR POLICY (2024)

        Section 1: General Code of Conduct
        All employees must maintain professional conduct and observe office hours from 9 AM to 6 PM.

        Section 2: Incident Management
        In the event of an IT systems disruption or unauthorized access, the IT helpdesk will investigate
        and inform leadership within 3 business days.

        Section 3: Workplace Conduct
        We strictly forbid harassment of any kind. Employees may report concerns directly to HR.
        """

        # 3. Execute End-to-End Audit
        result = self.orchestrator.run_compliance_audit(
            organization_id="ORG-CM-100",
            business_profile=profile,
            document_text=document_text,
            document_date="2024-06-01",
            audit_query="Audit workplace and cybersecurity compliance for IT operations in India.",
        )

        # 4. Assert Audit Outcome
        self.assertEqual(result.status, "SUCCESS")
        self.assertGreater(len(result.findings), 0)
        self.assertGreater(len(result.action_plans), 0)
        self.assertGreater(result.confidence.overall_confidence, 0.70)
        self.assertTrue(result.requires_professional_review)
        self.assertIn("ComplyAI continuously expands its jurisdiction-specific", result.disclaimer)

        # Check CERT-In finding detection
        certin_findings = [f for f in result.findings if "CYBERSECURITY" in f.category or "CERT" in f.requirement]
        self.assertGreater(len(certin_findings), 0)
        self.assertIn("6 hours", certin_findings[0].requirement)
        self.assertEqual(certin_findings[0].risk, RiskLevel.HIGH)

        # Check POSH finding detection (35 employees >= 10 workers threshold)
        posh_findings = [f for f in result.findings if "LABOUR" in f.category or "Complaints Committee" in f.requirement]
        self.assertGreater(len(posh_findings), 0)

        # Check Action Plans
        self.assertEqual(len(result.action_plans), len(result.findings))
        first_plan = result.action_plans[0]
        self.assertIn(first_plan.priority, [1, 2, 3])
        self.assertTrue(first_plan.professional_review)

        # 5. Check Reproducibility Audit Trail
        saved_log = self.repo.get_audit_log(result.audit_id)
        self.assertIsNotNone(saved_log)
        self.assertEqual(saved_log["audit_id"], result.audit_id)
        self.assertEqual(saved_log["reproducibility_metadata"]["engine_version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()


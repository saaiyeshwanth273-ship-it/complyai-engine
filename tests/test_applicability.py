"""Tests for Applicability Engine and Temporal Reasoning Engine.
"""
import unittest
from complyai.connectors.india import IndiaConnector
from complyai.connectors.eu import EUConnector
from complyai.reasoning.applicability import ApplicabilityEngine
from complyai.reasoning.temporal import TemporalReasoningEngine
from complyai.types import BusinessProfile, LegalDocument, SourceStatus


class TestApplicabilityAndTemporal(unittest.TestCase):

    def setUp(self):
        self.app_engine = ApplicabilityEngine()
        self.temp_engine = TemporalReasoningEngine()
        self.india_conn = IndiaConnector()
        self.eu_conn = EUConnector()

    def test_posh_headcount_threshold(self):
        posh_doc = self.india_conn.parse_source(self.india_conn.fetch_source("IND-POSH-2013"))

        # Business 1: 5 employees (Below threshold >= 10 workers)
        small_business = BusinessProfile(company_name="Small Startup", employee_count=5)
        res_small = self.app_engine.evaluate(small_business, posh_doc)
        self.assertFalse(res_small.applicable)

        # Business 2: 25 employees (Above threshold >= 10 workers)
        mid_business = BusinessProfile(company_name="Midscale IT", employee_count=25)
        res_mid = self.app_engine.evaluate(mid_business, posh_doc)
        self.assertTrue(res_mid.applicable)

    def test_csr_turnover_threshold(self):
        co_doc = self.india_conn.parse_source(self.india_conn.fetch_source("IND-COMPANIES-2013"))
        csr_req = co_doc.sections[1].requirements[0]

        # Business with 50 Cr turnover (Below 1000 Cr threshold)
        profile_low = BusinessProfile(company_name="Tech Solutions", turnover_inr=500_000_000.0)
        res_low = self.app_engine.evaluate(profile_low, co_doc, requirement=csr_req)
        self.assertFalse(res_low.applicable)

        # Business with 1200 Cr turnover (Above 1000 Cr threshold)
        profile_high = BusinessProfile(company_name="Global Giant", turnover_inr=12_000_000_000.0)
        res_high = self.app_engine.evaluate(profile_high, co_doc, requirement=csr_req)
        self.assertTrue(res_high.applicable)

    def test_extraterritorial_eu_gdpr_check(self):
        gdpr_doc = self.eu_conn.parse_source(self.eu_conn.fetch_source("EU-GDPR-2016-679"))

        # Indian SaaS selling purely in India
        pure_domestic = BusinessProfile(company_name="Local Store", country="India", customers=["India"])
        res_domestic = self.app_engine.evaluate(pure_domestic, gdpr_doc)
        self.assertFalse(res_domestic.applicable)

        # Indian SaaS selling to EU customers
        saas_export = BusinessProfile(company_name="Global SaaS", country="India", customers=["EU"])
        res_export = self.app_engine.evaluate(saas_export, gdpr_doc)
        self.assertTrue(res_export.applicable)
        self.assertTrue(res_export.requires_human_review)

    def test_temporal_reasoning_historical_evaluation(self):
        dpdpa_doc = self.india_conn.parse_source(self.india_conn.fetch_source("IND-DPDPA-2023"))

        # Evaluating conduct from 2021 (before DPDPA enacted in August 2023)
        check_2021 = self.temp_engine.is_effective_at(dpdpa_doc, "2021-05-10")
        self.assertFalse(check_2021["in_force"])
        self.assertEqual(check_2021["status"], "FUTURE_LAW_AT_DATE")

        # Evaluating conduct from 2024 (in force)
        check_2024 = self.temp_engine.is_effective_at(dpdpa_doc, "2024-01-15")
        self.assertTrue(check_2024["in_force"])
        self.assertEqual(check_2024["status"], "IN_FORCE")


if __name__ == "__main__":
    unittest.main()


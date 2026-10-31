"""Unit tests for Regulatory Connectors across India and International Jurisdictions.
"""
import unittest
from complyai.connectors.india import IndiaConnector
from complyai.connectors.eu import EUConnector
from complyai.connectors.us_federal import USFederalConnector, USStateConnector
from complyai.connectors.international import (
    UKConnector,
    SingaporeConnector,
    AustraliaConnector,
    CanadaConnector,
    UAEConnector,
    ILOConnector,
    OECDConnector,
)
from complyai.types import InstrumentType, SourceStatus


class TestRegulatoryConnectors(unittest.TestCase):

    def test_india_connector(self):
        conn = IndiaConnector()
        sources = conn.discover_sources()
        self.assertGreater(len(sources), 3)

        # Ingest DPDPA 2023
        raw_dpdpa = conn.fetch_source("IND-DPDPA-2023")
        doc = conn.parse_source(raw_dpdpa)
        self.assertEqual(doc.short_title, "DPDPA 2023")
        self.assertEqual(doc.jurisdiction, "India")
        self.assertEqual(doc.status, SourceStatus.VERIFIED)
        self.assertGreater(len(doc.sections), 0)

    def test_eu_connector(self):
        conn = EUConnector()
        sources = conn.discover_sources()
        self.assertTrue(any(s["source_id"] == "EU-GDPR-2016-679" for s in sources))

        raw_gdpr = conn.fetch_source("EU-GDPR-2016-679")
        doc = conn.parse_source(raw_gdpr)
        self.assertEqual(doc.jurisdiction, "European Union")
        self.assertEqual(doc.instrument_type, InstrumentType.REGULATION)

    def test_us_connectors(self):
        fed_conn = USFederalConnector()
        fed_doc = fed_conn.parse_source(fed_conn.fetch_source("US-FED-FLSA"))
        self.assertEqual(fed_doc.jurisdiction, "United States:Federal")

        ca_conn = USStateConnector(state="California")
        ca_doc = ca_conn.parse_source(ca_conn.fetch_source("US-CA-CCPA"))
        self.assertEqual(ca_doc.jurisdiction, "United States:California")

    def test_international_connectors(self):
        uk_doc = UKConnector().parse_source(UKConnector().fetch_source("UK-DPA-2018"))
        self.assertEqual(uk_doc.jurisdiction, "United Kingdom")

        sg_doc = SingaporeConnector().parse_source(SingaporeConnector().fetch_source("SG-PDPA-2012"))
        self.assertEqual(sg_doc.jurisdiction, "Singapore")

        au_doc = AustraliaConnector().parse_source(AustraliaConnector().fetch_source("AU-PRIVACY-1988"))
        self.assertEqual(au_doc.jurisdiction, "Australia")

        ca_doc = CanadaConnector().parse_source(CanadaConnector().fetch_source("CA-PIPEDA-2000"))
        self.assertEqual(ca_doc.jurisdiction, "Canada:Federal")

        uae_doc = UAEConnector(zone="Mainland").parse_source(UAEConnector(zone="Mainland").fetch_source("UAE-PDPL-45-2021"))
        self.assertEqual(uae_doc.jurisdiction, "UAE:Mainland")

    def test_ilo_connector_treaty_distinction(self):
        ilo_conn = ILOConnector()
        raw = ilo_conn.fetch_source("ILO-C138")
        doc = ilo_conn.parse_source(raw)
        self.assertEqual(doc.instrument_type, InstrumentType.CONVENTION)
        self.assertEqual(doc.short_title, "ILO C138")

    def test_oecd_connector(self):
        oecd_conn = OECDConnector()
        raw = oecd_conn.fetch_source("OECD-PILLAR2-GLOBE")
        doc = oecd_conn.parse_source(raw)
        self.assertEqual(doc.instrument_type, InstrumentType.FRAMEWORK)


if __name__ == "__main__":
    unittest.main()


"""Seed script for UK, Singapore, Australia, Canada, UAE, and OECD frameworks.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from complyai.connectors.international import (
    UKConnector,
    SingaporeConnector,
    AustraliaConnector,
    CanadaConnector,
    UAEConnector,
    OECDConnector,
)
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService


def seed_international(repo: RegulatoryRepository = None) -> RegulatoryRepository:
    if repo is None:
        repo = RegulatoryRepository()
    ingestion = RegulatoryIngestionService(repository=repo)
    connectors = [
        UKConnector(),
        SingaporeConnector(),
        AustraliaConnector(),
        CanadaConnector(),
        UAEConnector(zone="Mainland"),
        OECDConnector(),
    ]

    print("[ComplyAI] Ingesting International Regulatory Sources...")
    for conn in connectors:
        for d in ingestion.ingest_all_from_connector(conn):
            print(f"  * Ingested: {d.title} ({d.short_title}) [{d.jurisdiction}]")
    return repo


if __name__ == "__main__":
    r = seed_international()
    print(f"Total documents in repository: {len(r.list_documents())}")


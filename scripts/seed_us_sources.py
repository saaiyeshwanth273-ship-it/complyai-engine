"""Seed script for US Federal (FLSA) & State (California CCPA) Regulatory Sources.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from complyai.connectors.us_federal import USFederalConnector, USStateConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService


def seed_us(repo: RegulatoryRepository = None) -> RegulatoryRepository:
    if repo is None:
        repo = RegulatoryRepository()
    ingestion = RegulatoryIngestionService(repository=repo)

    print("[ComplyAI] Ingesting US Federal Regulatory Sources...")
    fed_connector = USFederalConnector()
    for d in ingestion.ingest_all_from_connector(fed_connector):
        print(f"  * Ingested: {d.title} ({d.short_title})")

    print("[ComplyAI] Ingesting California State Regulatory Sources...")
    ca_connector = USStateConnector(state="California")
    for d in ingestion.ingest_all_from_connector(ca_connector):
        print(f"  * Ingested: {d.title} ({d.short_title})")
    return repo


if __name__ == "__main__":
    r = seed_us()
    print(f"Total documents in repository: {len(r.list_documents())}")


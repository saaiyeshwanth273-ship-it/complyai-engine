"""Seed script for Authoritative European Union Regulatory Sources (GDPR, EU AI Act).
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from complyai.connectors.eu import EUConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService


def seed_eu(repo: RegulatoryRepository = None) -> RegulatoryRepository:
    if repo is None:
        repo = RegulatoryRepository()
    ingestion = RegulatoryIngestionService(repository=repo)
    connector = EUConnector()

    print("[ComplyAI] Ingesting EU Regulatory Sources...")
    docs = ingestion.ingest_all_from_connector(connector)
    for d in docs:
        print(f"  * Ingested: {d.title} ({d.short_title}) - Authority: {d.authority} [Status: {d.status.value}]")
    return repo


if __name__ == "__main__":
    r = seed_eu()
    print(f"Total documents in repository: {len(r.list_documents())}")


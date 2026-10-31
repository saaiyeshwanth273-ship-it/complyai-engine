"""Seed script for Authoritative Indian Central and State Regulatory Sources.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from complyai.connectors.india import IndiaConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService


def seed_india(repo: RegulatoryRepository = None) -> RegulatoryRepository:
    if repo is None:
        repo = RegulatoryRepository()
    ingestion = RegulatoryIngestionService(repository=repo)
    connector = IndiaConnector()

    print("[ComplyAI] Ingesting India Central Regulatory Sources...")
    docs = ingestion.ingest_all_from_connector(connector)
    for d in docs:
        print(f"  * Ingested: {d.title} ({d.short_title}) - Authority: {d.authority} [Status: {d.status.value}]")
    return repo


if __name__ == "__main__":
    r = seed_india()
    print(f"Total documents in repository: {len(r.list_documents())}")


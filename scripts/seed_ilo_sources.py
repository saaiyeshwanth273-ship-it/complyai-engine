"""Seed script for International Labour Organization (ILO) Conventions.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from complyai.connectors.international import ILOConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService


def seed_ilo(repo: RegulatoryRepository = None) -> RegulatoryRepository:
    if repo is None:
        repo = RegulatoryRepository()
    ingestion = RegulatoryIngestionService(repository=repo)
    connector = ILOConnector()

    print("[ComplyAI] Ingesting ILO Conventions...")
    docs = ingestion.ingest_all_from_connector(connector)
    for d in docs:
        print(f"  * Ingested: {d.title} ({d.short_title}) - Type: {d.instrument_type.value}")
    return repo


if __name__ == "__main__":
    r = seed_ilo()
    print(f"Total documents in repository: {len(r.list_documents())}")


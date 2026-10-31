"""Base Connector Interface and metadata models for regulatory sources.
"""
from __future__ import annotations

import abc
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from complyai.types import (
    InstrumentType,
    LegalDocument,
    LegalDomain,
    LegalRequirement,
    LegalSection,
    SourceHierarchy,
    SourceStatus,
)


class BaseRegulatoryConnector(abc.ABC):
    """Abstract Base Class for Jurisdiction Regulatory Connectors."""

    def __init__(self, jurisdiction: str):
        self.jurisdiction = jurisdiction

    @abc.abstractmethod
    def discover_sources(self) -> List[Dict[str, Any]]:
        """Scans / queries official registries or gazettes to find available regulatory documents."""
        pass

    @abc.abstractmethod
    def fetch_source(self, source_id: str) -> Dict[str, Any]:
        """Fetches raw text, XML, or PDF contents from official repository or cache."""
        pass

    @abc.abstractmethod
    def parse_source(self, raw_data: Dict[str, Any]) -> LegalDocument:
        """Parses raw text/structure into standardized LegalDocument with sections."""
        pass

    @abc.abstractmethod
    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts authority, effective dates, instrument type, and jurisdiction scope."""
        pass

    @abc.abstractmethod
    def detect_changes(self, source_id: str, existing_checksum: str) -> Dict[str, Any]:
        """Compares official source hash with existing checksum to detect amendments or repeals."""
        pass

    def compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


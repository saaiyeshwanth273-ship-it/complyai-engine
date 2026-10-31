"""Configuration settings for ComplyAI Regulatory Engine.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    # Model configuration
    GEMMA_MODEL: str = os.getenv("GEMMA_MODEL", "google/gemma-2-9b-it")
    GEMMA_QUANTIZATION: str = os.getenv("GEMMA_QUANTIZATION", "4bit")
    GEMMA_MAX_TOKENS: int = int(os.getenv("GEMMA_MAX_TOKENS", "4096"))
    GEMMA_TEMPERATURE: float = float(os.getenv("GEMMA_TEMPERATURE", "0.1"))
    GEMMA_INFERENCE_BACKEND: str = os.getenv("GEMMA_INFERENCE_BACKEND", "mock")  # mock, ollama, transformers, vllm, vertex

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///complyai.db")
    PGVECTOR_ENABLED: bool = os.getenv("PGVECTOR_ENABLED", "false").lower() == "true"

    # Embedding configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "legal-bert-multilingual-v1")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    # RAG parameters
    BM25_K1: float = float(os.getenv("BM25_K1", "1.5"))
    BM25_B: float = float(os.getenv("BM25_B", "0.75"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    RERANKER_TOP_N: int = int(os.getenv("RERANKER_TOP_N", "5"))

    # Verification and safety thresholds
    GROUNDING_THRESHOLD: float = float(os.getenv("GROUNDING_THRESHOLD", "0.75"))
    CITATION_MATCH_THRESHOLD: float = float(os.getenv("CITATION_MATCH_THRESHOLD", "0.70"))
    STRICT_CITATION_VERIFICATION: bool = True
    HUMAN_REVIEW_RISK_THRESHOLD: str = "HIGH"

    # App meta
    ENGINE_VERSION: str = "1.0.0"
    PROMPT_VERSION: str = "2026.1"
    KNOWLEDGE_BASE_VERSION: str = "v1.2-india-intl"

    # Legal Disclaimer mandated by Section 102
    LEGAL_DISCLAIMER: str = (
        "ComplyAI continuously expands its jurisdiction-specific regulatory knowledge base. "
        "Coverage depends on available authoritative sources and should not be interpreted as exhaustive legal coverage. "
        "ComplyAI is an AI regulatory intelligence tool and does not provide formal legal advice or substitute for licensed legal counsel."
    )


settings = Settings()


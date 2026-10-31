"""Model Router directing different compliance subtasks to optimal model tiers.
Small model -> document classification & tokenization
Efficient model -> structured clause & requirement extraction
Gemma -> deep legal reasoning & synthesis
Reranker -> cross-encoder relevance
"""
from __future__ import annotations

from typing import Any, Dict


class ModelRouter:
    """Routes regulatory reasoning requests based on computational complexity and risk level."""

    def route_task(self, task_type: str, risk_level: str = "LOW", is_uncertain: bool = False) -> Dict[str, Any]:
        if task_type in ["CLASSIFICATION", "INTENT_DETECTION", "KEYWORD_EXTRACTION"]:
            return {
                "tier": "SMALL_MODEL",
                "recommended_model": "gemma-2-2b-it",
                "quantization": "4bit",
                "description": "Fast keyword and domain classification.",
            }
        elif task_type in ["CLAUSE_EXTRACTION", "REQUIREMENT_PARSING"]:
            return {
                "tier": "EFFICIENT_MODEL",
                "recommended_model": "gemma-2-9b-it",
                "quantization": "4bit",
                "description": "Structured extraction of obligations, exceptions, and deadlines.",
            }
        elif task_type in ["COMPLIANCE_REASONING", "CROSS_BORDER_ANALYSIS"]:
            if risk_level in ["HIGH", "CRITICAL"] or is_uncertain:
                return {
                    "tier": "PREMIUM_REASONING",
                    "recommended_model": "gemma-2-27b-it",
                    "quantization": "8bit",
                    "requires_deep_validation": True,
                    "description": "High-risk compliance gap reasoning with double citation verification.",
                }
            return {
                "tier": "STANDARD_REASONING",
                "recommended_model": "gemma-2-9b-it",
                "quantization": "4bit",
                "requires_deep_validation": True,
                "description": "Standard compliance gap synthesis with citation verification.",
            }
        else:
            return {
                "tier": "STANDARD_REASONING",
                "recommended_model": "gemma-2-9b-it",
                "quantization": "4bit",
                "description": "General task fallback.",
            }


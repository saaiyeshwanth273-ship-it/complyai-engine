"""Action Plan Generator transforming compliance gaps into practical, prioritized remediations.
"""
from __future__ import annotations

from typing import List, Optional
from complyai.types import ActionPlanItem, LegalRequirement, RiskLevel


class ActionPlanner:
    """Translates identified compliance gaps and findings into plain-language action plans."""

    def generate_plan(
        self,
        finding_id: str,
        problem: str,
        requirement: LegalRequirement,
        risk: RiskLevel,
    ) -> ActionPlanItem:
        # Determine priority based on risk
        priority = 1 if risk in (RiskLevel.CRITICAL, RiskLevel.HIGH) else (2 if risk == RiskLevel.MEDIUM else 3)

        why_it_matters = (
            f"Under {requirement.source_title} ({requirement.source_section}), "
            f"{requirement.subject} is required to {requirement.action} {requirement.object}. "
            f"Non-alignment may lead to regulatory inquiries or statutory non-compliance exposure."
        )

        steps = [
            f"Review current operational practices regarding {requirement.object}.",
            f"Update organizational policy / standard operating procedures to explicitly incorporate {requirement.action}.",
        ]

        if requirement.deadline:
            steps.append(f"Ensure workflows adhere to statutory timeframe: {requirement.deadline}.")

        steps.append("Consult qualified legal counsel / compliance officer for formal sign-off.")

        return ActionPlanItem(
            problem=problem,
            why_it_matters=why_it_matters,
            recommended_steps=steps,
            priority=priority,
            owner="Legal / Compliance Team",
            deadline="30 Days" if priority == 1 else "60 Days",
            professional_review=True,
            associated_finding_id=finding_id,
        )


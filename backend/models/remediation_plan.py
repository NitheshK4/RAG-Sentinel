from typing import Any
from pydantic import BaseModel, Field


class RemediationAction(BaseModel):
    action: str
    priority: int
    reason: str
    requires_human_approval: bool


class RemediationPlanInput(BaseModel):
    incident_report: Any = Field(..., description="Output from incident reporter")
    asset_inventory: Any = Field(default=None, description="Inventory of affected assets")
    operational_constraints: str = Field(default="", description="Operational constraints for remediation")
    available_actions: list[str] = Field(
        default_factory=lambda: [
            "quarantine_source", "remove_chunks", "apply_retrieval_block",
            "reindex_collection", "shadow_index_promotion", "notify_users"
        ]
    )
    reindex_capability: str = Field(default="full", description="Whether reindex is available: none, partial, full")


class RemediationPlanOutput(BaseModel):
    incident_id: str
    immediate_actions: list[RemediationAction]
    short_term_actions: list[RemediationAction]
    long_term_actions: list[RemediationAction]
    reindex_recommendation: str
    monitoring_recommendations: list[str]
    rollback_risk_notes: list[str]

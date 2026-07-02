from typing import Literal, Any
from pydantic import BaseModel, Field


class IncidentReportInput(BaseModel):
    incident_id: str = Field(..., description="Unique incident identifier")
    attack_hypothesis: Any = Field(..., description="Output from attack hypothesis builder")
    source_triage_output: Any = Field(None, description="Output from source triage")
    chunk_audit_outputs: list[Any] = Field(default_factory=list)
    retrieval_investigation_output: Any = Field(None, description="Output from retrieval trace investigation")
    business_context: str = Field(default="", description="Business context for impact assessment")


class IncidentReportOutput(BaseModel):
    incident_id: str
    title: str
    executive_summary: str
    severity: Literal["low", "medium", "high", "critical"]
    attack_family: str
    scope: list[str]
    confirmed_findings: list[str]
    suspected_findings: list[str]
    business_impact: str
    affected_assets: list[str]
    timeline_summary: list[str]
    recommended_immediate_actions: list[str]

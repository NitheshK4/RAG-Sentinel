from typing import Literal, Any
from pydantic import BaseModel, Field


class AttackHypothesisInput(BaseModel):
    source_triage_output: Any = Field(..., description="Output from source intake triage")
    chunk_audit_outputs: list[Any] = Field(default_factory=list, description="Outputs from chunk audits")
    retrieval_investigation_output: Any = Field(None, description="Output from retrieval trace investigation")
    feature_summary: str = Field(default="", description="Summary of extracted features")
    incident_scope: str = Field(..., description="Scope of the suspected incident")


class AttackHypothesisOutput(BaseModel):
    incident_scope: str
    primary_hypothesis: str
    primary_attack_family: Literal[
        "instruction_injection", "authority_spoofing", "near_duplicate_flooding",
        "contradiction_injection", "answer_hijacking", "query_baiting",
        "ranking_manipulation", "unknown"
    ]
    supporting_evidence: list[str]
    alternative_hypotheses: list[str]
    why_not_benign: list[str]
    confidence: float
    recommended_severity: Literal["low", "medium", "high", "critical"]

from typing import Literal
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    field: str
    snippet: str
    reason: str


class SourceTriageInput(BaseModel):
    source_id: str = Field(..., description="Unique source identifier")
    source_uri: str = Field(..., description="URI or upload path of the source")
    source_type: str = Field(..., description="e.g. markdown, pdf, html")
    collection_method: str = Field(..., description="e.g. user_upload, connector, crawler")
    owner: str = Field(default="unknown", description="Owner or author of the source")
    retrieved_metadata: dict = Field(default_factory=dict, description="Metadata attached to the source")
    document_excerpt: str = Field(..., description="Short text excerpt from the document")
    connector_trust_tier: Literal["high", "medium", "low", "unknown"] = Field(..., description="Trust tier of the connector")


class SourceTriageOutput(BaseModel):
    source_id: str
    trust_tier_assessment: Literal["high", "medium", "low", "unknown"]
    provenance_gaps: list[str]
    suspicious_signals: list[str]
    benign_signals: list[str]
    primary_attack_family: Literal[
        "instruction_injection", "authority_spoofing", "near_duplicate_flooding",
        "contradiction_injection", "answer_hijacking", "query_baiting",
        "ranking_manipulation", "unknown"
    ]
    severity: Literal["low", "medium", "high", "critical"]
    routing_decision: Literal["allow", "review", "shadow", "quarantine"]
    evidence: list[EvidenceItem]
    analyst_notes: str

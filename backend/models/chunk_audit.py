from typing import Literal
from pydantic import BaseModel, Field


class ChunkEvidence(BaseModel):
    snippet: str
    reason: str


class ChunkAuditInput(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    chunk_text: str = Field(..., description="Raw text of the chunk")
    section_title: str = Field(default="", description="Title of the section containing this chunk")
    source_summary: str = Field(default="", description="Brief description of the source document")
    neighbor_titles: list[str] = Field(default_factory=list, description="Titles of neighboring sections")
    metadata_features: dict = Field(default_factory=dict, description="Extracted metadata features")


class ChunkAuditOutput(BaseModel):
    chunk_id: str
    risk_label: Literal["clean", "suspicious", "poisoned", "ambiguous"]
    severity: Literal["low", "medium", "high", "critical"]
    attack_families: list[str]
    manipulation_targets: list[str]
    suspicious_signals: list[str]
    benign_explanations: list[str]
    requires_neighbor_audit: bool
    evidence: list[ChunkEvidence]
    final_reasoning_summary: str

from typing import Any
from pydantic import BaseModel, Field


class OrchestrationInput(BaseModel):
    stage: str = Field(..., description="Current pipeline stage name")
    payload_summary: str = Field(..., description="Brief summary of available payload")
    available_artifacts: dict = Field(default_factory=dict, description="Available artifacts for this stage")
    required_schema: str = Field(..., description="Name of the required output schema")
    escalation_policy: str = Field(default="review_on_missing_fields")


class OrchestrationOutput(BaseModel):
    route_name: str
    prompt_file: str
    minimal_input_bundle: dict[str, Any]
    skipped_fields: list[str]
    escalation_required: bool
    execution_notes: list[str]

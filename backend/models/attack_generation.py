from typing import Literal
from pydantic import BaseModel, Field


class AttackGenerationInput(BaseModel):
    clean_chunk: str = Field(..., description="The original clean chunk text")
    source_context: str = Field(default="", description="Brief description of the source document context")
    target_attack_family: Literal[
        "instruction_injection", "authority_spoofing", "near_duplicate_flooding",
        "contradiction_injection", "answer_hijacking", "query_baiting", "ranking_manipulation"
    ] = Field(..., description="Which attack family to inject")
    attack_goal: str = Field(..., description="What the attack is trying to achieve")
    target_query_family: str = Field(..., description="The type of query this attack targets")
    difficulty_level: Literal["easy", "medium", "hard"] = Field(default="medium")


class AttackGenerationOutput(BaseModel):
    attack_family: Literal[
        "instruction_injection", "authority_spoofing", "near_duplicate_flooding",
        "contradiction_injection", "answer_hijacking", "query_baiting", "ranking_manipulation"
    ]
    difficulty_level: Literal["easy", "medium", "hard"]
    mutated_chunk: str
    mutation_summary: str
    attack_goal: str
    target_query_family: str
    benchmark_label_notes: list[str]

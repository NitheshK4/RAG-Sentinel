from typing import Literal, Any
from pydantic import BaseModel, Field


class AttackFamilyScore(BaseModel):
    attack_family: str
    assessment: str


class BenchmarkScoreInput(BaseModel):
    benchmark_manifest: Any = Field(..., description="Benchmark test set manifest")
    detector_outputs: Any = Field(..., description="Detector outputs for each benchmark item")
    ground_truth_labels: Any = Field(..., description="Ground truth labels for benchmark items")
    retrieval_replay_metrics: Any = Field(default=None, description="Metrics from retrieval replay")
    run_metadata: dict = Field(default_factory=dict, description="Metadata about the benchmark run")


class BenchmarkScoreOutput(BaseModel):
    run_id: str
    overall_assessment: str
    strengths: list[str]
    weaknesses: list[str]
    attack_family_scores: list[AttackFamilyScore]
    answer_protection_assessment: str
    recommended_next_steps: list[str]
    release_readiness: Literal["not_ready", "staging_only", "production_candidate"]

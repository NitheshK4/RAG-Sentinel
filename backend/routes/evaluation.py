from fastapi import APIRouter
from backend.core.llm_client import call_llm
from backend.core.prompt_loader import load_prompt
from backend.models.attack_generation import AttackGenerationInput, AttackGenerationOutput
from backend.models.benchmark_score import BenchmarkScoreInput, BenchmarkScoreOutput

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post("/attack-generator", response_model=AttackGenerationOutput, summary="Poisoning Attack Generator")
async def attack_generator(payload: AttackGenerationInput):
    """
    Generate realistic, labeled poisoning examples from clean source material.
    Used for benchmark creation and red-team testing.
    """
    prompt = load_prompt("evaluation/01_poisoning_attack_generator.md", {
        "clean_chunk": payload.clean_chunk,
        "source_context": payload.source_context,
        "target_attack_family": payload.target_attack_family,
        "attack_goal": payload.attack_goal,
        "target_query_family": payload.target_query_family,
        "difficulty_level": payload.difficulty_level,
    })
    result = await call_llm(prompt, "attack_generator")
    return AttackGenerationOutput(**result)


@router.post("/benchmark-judge", response_model=BenchmarkScoreOutput, summary="Benchmark Judge")
async def benchmark_judge(payload: BenchmarkScoreInput):
    """
    Score a detector run over a poisoning benchmark.
    Explains wins, misses, and failure modes per attack family.
    """
    prompt = load_prompt("evaluation/02_benchmark_judge.md", {
        "benchmark_manifest": payload.benchmark_manifest,
        "detector_outputs": payload.detector_outputs,
        "ground_truth_labels": payload.ground_truth_labels,
        "retrieval_replay_metrics": payload.retrieval_replay_metrics,
        "run_metadata": payload.run_metadata,
    })
    result = await call_llm(prompt, "benchmark_judge")
    return BenchmarkScoreOutput(**result)

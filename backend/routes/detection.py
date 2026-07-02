from fastapi import APIRouter
from backend.core.llm_client import call_llm
from backend.core.prompt_loader import load_prompt
from backend.models.chunk_audit import ChunkAuditInput, ChunkAuditOutput
from backend.models.retrieval_investigation import RetrievalInvestigationInput, RetrievalInvestigationOutput
from backend.models.attack_hypothesis import AttackHypothesisInput, AttackHypothesisOutput

router = APIRouter(prefix="/detection", tags=["Detection"])


class NeighborAuditInput(ChunkAuditInput):
    preceding_chunk: str = ""
    following_chunk: str = ""
    document_summary: str = ""
    source_trust_context: str = ""
    known_policies_or_facts: str = ""


@router.post("/neighbor-audit", response_model=ChunkAuditOutput, summary="Neighbor Consistency Audit")
async def neighbor_audit(payload: NeighborAuditInput):
    """
    Determine whether a suspicious chunk is inconsistent with its neighbors.
    Detects spoofed insertions, tone shifts, and factual contradictions.
    """
    prompt = load_prompt("detection/01_neighbor_consistency_audit.md", {
        "focus_chunk": payload.chunk_text,
        "preceding_chunk": payload.preceding_chunk,
        "following_chunk": payload.following_chunk,
        "document_summary": payload.document_summary,
        "source_trust_context": payload.source_trust_context,
        "known_policies_or_facts": payload.known_policies_or_facts,
    })
    result = await call_llm(prompt, "neighbor_audit")
    return ChunkAuditOutput(**result)


@router.post("/retrieval-trace", response_model=RetrievalInvestigationOutput, summary="Retrieval Trace Investigator")
async def retrieval_trace(payload: RetrievalInvestigationInput):
    """
    Analyze a retrieval trace to detect ranking domination, answer corruption,
    and query pattern exploitation.
    """
    prompt = load_prompt("detection/02_retrieval_trace_investigator.md", {
        "query": payload.query,
        "top_k_results": [r.model_dump() for r in payload.top_k_results],
        "pre_attack_baseline_results": [r.model_dump() for r in payload.pre_attack_baseline_results],
        "final_answer": payload.final_answer,
        "baseline_answer": payload.baseline_answer,
        "source_trust_map": payload.source_trust_map,
        "retrieval_metrics": payload.retrieval_metrics.model_dump(),
    })
    result = await call_llm(prompt, "retrieval_trace")
    return RetrievalInvestigationOutput(**result)


@router.post("/attack-hypothesis", response_model=AttackHypothesisOutput, summary="Attack Hypothesis Builder")
async def attack_hypothesis(payload: AttackHypothesisInput):
    """
    Synthesize evidence from content audits and retrieval traces into a
    concise, analyst-verifiable poisoning hypothesis.
    """
    prompt = load_prompt("detection/03_attack_hypothesis_builder.md", {
        "source_triage_output": payload.source_triage_output,
        "chunk_audit_outputs": payload.chunk_audit_outputs,
        "retrieval_investigation_output": payload.retrieval_investigation_output,
        "feature_summary": payload.feature_summary,
        "incident_scope": payload.incident_scope,
    })
    result = await call_llm(prompt, "attack_hypothesis")
    return AttackHypothesisOutput(**result)

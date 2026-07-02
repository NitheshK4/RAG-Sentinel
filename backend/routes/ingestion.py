from fastapi import APIRouter
from backend.core.llm_client import call_llm
from backend.core.prompt_loader import load_prompt
from backend.models.source_triage import SourceTriageInput, SourceTriageOutput
from backend.models.chunk_audit import ChunkAuditInput, ChunkAuditOutput

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post("/source-triage", response_model=SourceTriageOutput, summary="Source Intake Triage")
async def source_triage(payload: SourceTriageInput):
    """
    Assess a source before chunking and indexing.
    Identifies trust signals, provenance gaps, and poisoning risk indicators.
    """
    prompt = load_prompt("ingestion/01_source_intake_triage.md", {
        "source_id": payload.source_id,
        "source_uri": payload.source_uri,
        "source_type": payload.source_type,
        "collection_method": payload.collection_method,
        "owner": payload.owner,
        "retrieved_metadata": payload.retrieved_metadata,
        "document_excerpt": payload.document_excerpt,
        "connector_trust_tier": payload.connector_trust_tier,
    })
    result = await call_llm(prompt, "source_triage")
    return SourceTriageOutput(**result)


@router.post("/chunk-audit", response_model=ChunkAuditOutput, summary="Chunk Semantic Audit")
async def chunk_audit(payload: ChunkAuditInput):
    """
    Inspect a single chunk for semantic poisoning signals.
    Detects instruction injection, answer hijacking, authority claims, and retrieval bait.
    """
    prompt = load_prompt("ingestion/02_chunk_semantic_audit.md", {
        "chunk_id": payload.chunk_id,
        "document_id": payload.document_id,
        "chunk_text": payload.chunk_text,
        "section_title": payload.section_title,
        "source_summary": payload.source_summary,
        "neighbor_titles": payload.neighbor_titles,
        "metadata_features": payload.metadata_features,
    })
    result = await call_llm(prompt, "chunk_audit")
    return ChunkAuditOutput(**result)

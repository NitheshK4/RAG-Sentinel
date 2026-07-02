from fastapi import APIRouter
from backend.core.llm_client import call_llm
from backend.core.prompt_loader import load_prompt
from backend.models.orchestration_route import OrchestrationInput, OrchestrationOutput

router = APIRouter(prefix="/orchestrate", tags=["Orchestrator"])


@router.post("", response_model=OrchestrationOutput, summary="Pipeline Orchestrator")
async def orchestrate(payload: OrchestrationInput):
    """
    Coordinate stage-specific prompt execution.
    Routes the request to the correct downstream prompt and prepares a minimal input bundle.
    """
    prompt = load_prompt("system/00_orchestrator.md", {
        "stage": payload.stage,
        "payload_summary": payload.payload_summary,
        "available_artifacts": payload.available_artifacts,
        "required_schema": payload.required_schema,
        "escalation_policy": payload.escalation_policy,
    })
    result = await call_llm(prompt, "orchestration")
    return OrchestrationOutput(**result)

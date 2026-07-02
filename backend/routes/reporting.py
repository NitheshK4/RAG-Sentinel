from fastapi import APIRouter
from backend.core.llm_client import call_llm
from backend.core.prompt_loader import load_prompt
from backend.models.incident_report import IncidentReportInput, IncidentReportOutput
from backend.models.remediation_plan import RemediationPlanInput, RemediationPlanOutput

router = APIRouter(prefix="/reporting", tags=["Reporting"])


@router.post("/incident-report", response_model=IncidentReportOutput, summary="Incident Reporter")
async def incident_report(payload: IncidentReportInput):
    """
    Produce an analyst-grade incident report from structured evidence.
    Summarizes scope, confirmed findings, business impact, and immediate actions.
    """
    prompt = load_prompt("reporting/01_incident_reporter.md", {
        "incident_id": payload.incident_id,
        "attack_hypothesis": payload.attack_hypothesis,
        "source_triage_output": payload.source_triage_output,
        "chunk_audit_outputs": payload.chunk_audit_outputs,
        "retrieval_investigation_output": payload.retrieval_investigation_output,
        "business_context": payload.business_context,
    })
    result = await call_llm(prompt, "incident_report")
    return IncidentReportOutput(**result)


@router.post("/remediation-plan", response_model=RemediationPlanOutput, summary="Remediation Planner")
async def remediation_plan(payload: RemediationPlanInput):
    """
    Generate a prioritized remediation plan balancing containment,
    false-positive risk, and recovery speed.
    """
    prompt = load_prompt("reporting/02_remediation_planner.md", {
        "incident_report": payload.incident_report,
        "asset_inventory": payload.asset_inventory,
        "operational_constraints": payload.operational_constraints,
        "available_actions": payload.available_actions,
        "reindex_capability": payload.reindex_capability,
    })
    result = await call_llm(prompt, "remediation_plan")
    return RemediationPlanOutput(**result)

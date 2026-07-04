"""
Demo routes — return pre-loaded sample data from examples/ directory.
These routes allow the analyst dashboard to demonstrate every pipeline
without requiring an LLM API key.
"""
import json
import csv
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.core.config import EXAMPLES_DIR, DEMO_MODE
from backend.core.llm_client import DEMO_RESPONSES

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.get("/status")
async def demo_status():
    """Return current mode (demo vs live LLM)."""
    return {
        "demo_mode": DEMO_MODE,
        "message": "Running in demo mode — all responses are realistic mock data." if DEMO_MODE
                   else "Running with live LLM API."
    }


@router.get("/sample-source-bundle")
async def sample_source_bundle():
    path = EXAMPLES_DIR / "sample-source-bundle.json"
    return json.loads(path.read_text())


@router.get("/sample-retrieval-trace")
async def sample_retrieval_trace():
    path = EXAMPLES_DIR / "sample-retrieval-trace.json"
    return json.loads(path.read_text())


@router.get("/sample-incident-report")
async def sample_incident_report():
    path = EXAMPLES_DIR / "sample-incident-report.json"
    return json.loads(path.read_text())


@router.get("/responses/{key}")
async def demo_response(key: str):
    """Return a specific demo response by key (e.g. 'source_triage', 'chunk_audit')."""
    if key not in DEMO_RESPONSES:
        return {"error": f"No demo response for key: {key}", "available_keys": list(DEMO_RESPONSES.keys())}
    return DEMO_RESPONSES[key]


import threading
from typing import Any

# In-memory database of incidents
_incidents: list[dict[str, Any]] = []
_incidents_lock = threading.Lock()


@router.get("/all-responses")
async def all_demo_responses():
    """Return all available demo response keys."""
    return {"available_keys": list(DEMO_RESPONSES.keys())}


@router.get("/incidents")
async def get_incidents():
    """Get all incident records from backend memory."""
    with _incidents_lock:
        return _incidents


@router.post("/incidents")
async def add_incident(incident: dict[str, Any]):
    """Add a new incident to backend memory."""
    with _incidents_lock:
        _incidents.insert(0, incident)
        if len(_incidents) > 50:  # Cap history length
            _incidents.pop()
    return {"status": "success"}


@router.delete("/incidents")
async def clear_incidents():
    """Clear all incident records from backend memory."""
    with _incidents_lock:
        _incidents.clear()
    return {"status": "success"}


@router.get("/incidents/export")
async def export_incidents(format: str = "json"):
    """Export current incidents as JSON or CSV file download."""
    with _incidents_lock:
        data = list(_incidents)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        # Write headers
        writer.writerow(["Timestamp", "Stage", "Title", "Severity", "Attack Family", "Summary"])
        # Write rows
        for item in data:
            d = item.get("data", {})
            writer.writerow([
                item.get("ts", ""),
                item.get("stage", ""),
                d.get("title") or d.get("primary_hypothesis") or f"{item.get('stage')} result",
                d.get("severity") or d.get("recommended_severity") or "low",
                d.get("attack_family") or d.get("primary_attack_family") or "",
                d.get("executive_summary") or d.get("primary_hypothesis") or d.get("overall_assessment") or ""
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=rag_sentinel_incidents.csv"}
        )
    else:
        # Default JSON
        return StreamingResponse(
            io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=rag_sentinel_incidents.json"}
        )




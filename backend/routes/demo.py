"""
Demo routes — return pre-loaded sample data from examples/ directory.
These routes allow the analyst dashboard to demonstrate every pipeline
without requiring an LLM API key.
"""
import json
import csv
import io
import datetime
import threading
from typing import Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.core.config import EXAMPLES_DIR, DEMO_MODE, DEFAULT_SETTINGS
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


# In-memory database of incidents
_incidents: list[dict[str, Any]] = []
_incidents_lock = threading.Lock()


@router.get("/all-responses")
async def all_demo_responses():
    """Return all available demo response keys."""
    return {"available_keys": list(DEMO_RESPONSES.keys())}


@router.get("/telemetry")
async def get_telemetry():
    """Get aggregated statistics of current incidents in memory."""
    with _incidents_lock:
        total = len(_incidents)
        by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        by_stage = {}
        by_attack_family = {}
        
        for item in _incidents:
            if not isinstance(item, dict):
                continue
            stage = item.get("stage", "unknown")
            by_stage[stage] = by_stage.get(stage, 0) + 1
            
            d = item.get("data")
            if isinstance(d, dict):
                sev = d.get("severity") or d.get("recommended_severity") or "low"
                sev_lower = str(sev).lower()
                if sev_lower in by_severity:
                    by_severity[sev_lower] += 1
                else:
                    by_severity[sev_lower] = by_severity.get(sev_lower, 0) + 1
                    
                family = d.get("attack_family") or d.get("primary_attack_family") or "none"
                by_attack_family[family] = by_attack_family.get(family, 0) + 1
                
        return {
            "total_incidents": total,
            "by_severity": by_severity,
            "by_stage": by_stage,
            "by_attack_family": by_attack_family
        }


@router.get("/threat-categories")
async def get_threat_categories():
    """Return all supported attack/threat families and their descriptions."""
    return {
        "categories": [
            {
                "id": "instruction_injection",
                "name": "Instruction Injection",
                "description": "Adversarial prompts embedded in document inputs targeting downstream LLM instruction overrides."
            },
            {
                "id": "authority_spoofing",
                "name": "Authority Spoofing",
                "description": "Forged provenance metadata or claiming administrative authority within content to compromise factuality."
            },
            {
                "id": "near_duplicate_flooding",
                "name": "Near-Duplicate Flooding",
                "description": "Stuffed duplicate or near-duplicate payloads targeting domination of retrieval spaces."
            },
            {
                "id": "semantic_drift",
                "name": "Semantic Drift",
                "description": "Gradual shifts in factuality or ontology mappings over multiple document revisions."
            },
            {
                "id": "retrieval_bait",
                "name": "Retrieval Bait",
                "description": "Engineering highly relevant terms designed to hijack semantic search ranking."
            }
        ]
    }


@router.get("/incidents")
async def get_incidents(
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "ts",
    order: str = "desc",
    severity: str = None
):
    """Get all incident records from backend memory with sorting, filtering, and pagination."""
    with _incidents_lock:
        # 1. Filter
        filtered_list = list(_incidents)
        if severity:
            sev_target = severity.lower()
            temp = []
            for item in filtered_list:
                d = item.get("data") or {}
                s = d.get("severity") or d.get("recommended_severity") or "low"
                if str(s).lower() == sev_target:
                    temp.append(item)
            filtered_list = temp
            
        # 2. Sort
        def get_sort_key(item):
            if sort_by == "severity":
                d = item.get("data") or {}
                s = str(d.get("severity") or d.get("recommended_severity") or "low").lower()
                sev_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                return sev_map.get(s, 0)
            elif sort_by == "stage":
                return item.get("stage", "")
            else:
                return item.get("ts", "")
                
        reverse_order = (order.lower() == "desc")
        filtered_list.sort(key=get_sort_key, reverse=reverse_order)
        
        # 3. Paginate
        paginated_list = filtered_list[offset : offset + limit]
        return paginated_list


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
            if not isinstance(item, dict):
                continue
            d = item.get("data")
            if not isinstance(d, dict):
                d = {}
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
    elif format == "html":
        # Create a basic but styled HTML table page
        html_content = """<html>
<head>
    <title>RAG Sentinel Incidents Export</title>
    <style>
        body { font-family: sans-serif; background-color: #121214; color: #e1e1e6; margin: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #29292e; padding: 10px; text-align: left; }
        th { background-color: #202024; color: #00d4ff; }
        tr:nth-child(even) { background-color: #17171a; }
    </style>
</head>
<body>
    <h1>RAG Sentinel Incident Report</h1>
    <table>
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Stage</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Attack Family</th>
                <th>Summary</th>
            </tr>
        </thead>
        <tbody>
"""
        for item in data:
            if not isinstance(item, dict):
                continue
            d = item.get("data")
            if not isinstance(d, dict):
                d = {}
            ts = item.get("ts", "")
            stage = item.get("stage", "")
            title = d.get("title") or d.get("primary_hypothesis") or f"{stage} result"
            severity = d.get("severity") or d.get("recommended_severity") or "low"
            attack_family = d.get("attack_family") or d.get("primary_attack_family") or ""
            summary = d.get("executive_summary") or d.get("primary_hypothesis") or d.get("overall_assessment") or ""
            html_content += f"""            <tr>
                <td>{ts}</td>
                <td>{stage}</td>
                <td>{title}</td>
                <td>{severity}</td>
                <td>{attack_family}</td>
                <td>{summary}</td>
            </tr>\n"""
        html_content += """        </tbody>
    </table>
</body>
</html>"""
        return StreamingResponse(
            io.BytesIO(html_content.encode("utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=rag_sentinel_incidents.html"}
        )
    else:
        # Default JSON
        return StreamingResponse(
            io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=rag_sentinel_incidents.json"}
        )


@router.get("/incidents/{index}")
async def get_incident_detail(index: int):
    """Get a single incident by its index in the store."""
    with _incidents_lock:
        if index < 0 or index >= len(_incidents):
            raise HTTPException(status_code=404, detail=f"Incident index {index} not found")
        return _incidents[index]


@router.delete("/incidents/{index}")
async def delete_incident(index: int):
    """Delete a single incident from backend memory by its index."""
    with _incidents_lock:
        if index < 0 or index >= len(_incidents):
            raise HTTPException(status_code=404, detail=f"Incident index {index} not found")
        _incidents.pop(index)
    return {"status": "success"}



@router.post("/incidents/{index}/notes")
async def add_incident_note(index: int, body: dict[str, Any]):
    """Append an analyst note/annotation to a specific incident."""
    note_text = body.get("note", "").strip()
    if not note_text:
        raise HTTPException(status_code=400, detail="Note text is required ('note' field)")

    with _incidents_lock:
        if index < 0 or index >= len(_incidents):
            raise HTTPException(status_code=404, detail=f"Incident index {index} not found")
        incident = _incidents[index]
        if "analyst_notes" not in incident:
            incident["analyst_notes"] = []
        incident["analyst_notes"].append({
            "note": note_text,
            "added_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
    return {"status": "success", "notes_count": len(incident["analyst_notes"])}


_settings = dict(DEFAULT_SETTINGS)
_settings_lock = threading.Lock()


@router.post("/settings/reset")
async def reset_settings():
    """Reset the dynamic security detection parameters to their default values."""
    with _settings_lock:
        _settings.clear()
        _settings.update(DEFAULT_SETTINGS)
    return {"status": "success", "settings": _settings}



@router.get("/settings")
async def get_settings():
    """Get the current dynamic security detection parameters."""
    with _settings_lock:
        return _settings


@router.post("/settings")
async def update_settings(settings: dict[str, Any]):
    """Update dynamic security detection parameters."""
    with _settings_lock:
        # Filter only valid keys
        invalid_keys = [k for k in settings if k not in _settings]
        if invalid_keys:
            raise HTTPException(status_code=400, detail=f"Invalid settings key(s): {', '.join(invalid_keys)}")

        updates = {}
        if "cosine_similarity_threshold" in settings:
            try:
                val = float(settings["cosine_similarity_threshold"])
                if not (0.0 <= val <= 1.0):
                    raise ValueError()
                updates["cosine_similarity_threshold"] = val
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail="cosine_similarity_threshold must be a float between 0.0 and 1.0"
                )

        if "neighbor_audit_depth" in settings:
            try:
                val = int(settings["neighbor_audit_depth"])
                if val <= 0:
                    raise ValueError()
                updates["neighbor_audit_depth"] = val
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail="neighbor_audit_depth must be a positive integer"
                )

        if "automatic_quarantine" in settings:
            v = settings["automatic_quarantine"]
            if isinstance(v, str):
                vl = v.lower()
                if vl in ("true", "1", "yes"):
                    updates["automatic_quarantine"] = True
                elif vl in ("false", "0", "no"):
                    updates["automatic_quarantine"] = False
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="automatic_quarantine must be a boolean or a valid boolean-like string"
                    )
            elif isinstance(v, bool):
                updates["automatic_quarantine"] = v
            elif isinstance(v, (int, float)):
                updates["automatic_quarantine"] = bool(v)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="automatic_quarantine must be a boolean or a valid boolean-like value"
                )

        if "anomaly_risk_tolerance" in settings:
            v = settings["anomaly_risk_tolerance"]
            if v not in ("low", "medium", "high"):
                raise HTTPException(
                    status_code=400,
                    detail="anomaly_risk_tolerance must be 'low', 'medium', or 'high'"
                )
            updates["anomaly_risk_tolerance"] = v

        _settings.update(updates)
    return {"status": "success", "settings": _settings}





"""
RAG Sentinel — Vector Index Poisoning Detector
FastAPI application entrypoint.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.core.config import APP_TITLE, APP_VERSION, API_PREFIX, DEMO_MODE
from backend.core.rate_limiter import RateLimitMiddleware
from backend.core.middleware import RequestIdMiddleware
from backend.routes import ingestion, detection, evaluation, reporting, orchestrator, demo

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mode = "DEMO (no LLM API key)" if DEMO_MODE else "LIVE (Gemini API)"
    logger.info(f"RAG Sentinel starting — mode: {mode}")
    yield
    logger.info("RAG Sentinel shutting down.")


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=(
        "Production-ready vector index poisoning detection system. "
        "Detects, investigates, and remediates malicious content in RAG pipelines."
    ),
    lifespan=lifespan,
)

# CORS — allow all for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — per-IP sliding window
app.add_middleware(RateLimitMiddleware)

# Request-ID correlation — traceability across logs
app.add_middleware(RequestIdMiddleware)

# API Routes
app.include_router(ingestion.router, prefix=API_PREFIX)
app.include_router(detection.router, prefix=API_PREFIX)
app.include_router(evaluation.router, prefix=API_PREFIX)
app.include_router(reporting.router, prefix=API_PREFIX)
app.include_router(orchestrator.router, prefix=API_PREFIX)
app.include_router(demo.router, prefix=API_PREFIX)


@app.exception_handler(FileNotFoundError)
async def filenotfound_exception_handler(request, exc):
    logger.error(f"File not found error: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": f"Required configuration or template file missing: {exc}"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )




@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "demo_mode": DEMO_MODE,
    }


@app.get("/api/v1/health/ready")
async def readiness():
    """
    Readiness probe — checks all critical dependencies.
    Returns 200 if all components are healthy, 503 if any are degraded.
    """
    checks: dict[str, dict] = {}

    # 1. LLM API connectivity
    if DEMO_MODE:
        checks["llm_api"] = {"status": "ok", "detail": "Demo mode — no LLM API required"}
    else:
        try:
            import httpx
            from backend.core.config import GEMINI_API_KEY, LLM_MODEL
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{LLM_MODEL}?key={GEMINI_API_KEY}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    checks["llm_api"] = {"status": "ok", "detail": f"Model {LLM_MODEL} reachable"}
                else:
                    checks["llm_api"] = {"status": "degraded", "detail": f"HTTP {resp.status_code}"}
        except Exception as e:
            checks["llm_api"] = {"status": "degraded", "detail": str(e)}

    # 2. Incident store
    try:
        from backend.routes.demo import _incidents, _incidents_lock
        with _incidents_lock:
            count = len(_incidents)
        checks["incident_store"] = {"status": "ok", "detail": f"{count} incidents in memory"}
    except Exception as e:
        checks["incident_store"] = {"status": "degraded", "detail": str(e)}

    # 3. Settings store
    try:
        from backend.routes.demo import _settings, _settings_lock
        with _settings_lock:
            _ = dict(_settings)
        checks["settings_store"] = {"status": "ok", "detail": "Settings accessible"}
    except Exception as e:
        checks["settings_store"] = {"status": "degraded", "detail": str(e)}

    all_ok = all(c["status"] == "ok" for c in checks.values())
    status_code = 200 if all_ok else 503

    from fastapi.responses import JSONResponse as _JSONResponse
    return _JSONResponse(
        status_code=status_code,
        content={
            "ready": all_ok,
            "checks": checks,
        },
    )


# Serve the frontend SPA
frontend_dir = Path(__file__).parent.parent / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dir / "index.html"))

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

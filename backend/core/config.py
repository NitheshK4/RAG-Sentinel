import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/core/config.py → backend/core → backend → project root
PROMPTS_DIR = BASE_DIR / "prompts"
SCHEMAS_DIR = BASE_DIR / "schemas"
EXAMPLES_DIR = BASE_DIR / "examples"

# LLM Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
DEMO_MODE = not bool(GEMINI_API_KEY)

# App Config
APP_TITLE = "RAG Sentinel — Vector Index Poisoning Detector"
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

DEFAULT_SETTINGS = {
    "cosine_similarity_threshold": 0.75,
    "anomaly_risk_tolerance": "medium",
    "neighbor_audit_depth": 3,
    "automatic_quarantine": False
}


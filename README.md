<div align="center">

<img src="https://img.shields.io/badge/RAG-Sentinel-00d4ff?style=for-the-badge&logo=shield&logoColor=white" alt="RAG Sentinel" height="40"/>

# RAG Sentinel — Vector Index Poisoning Detector

**A production-grade AI security analyst console for detecting, investigating, and remediating vector index poisoning attacks in Retrieval-Augmented Generation pipelines.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![CI](https://github.com/NitheshK4/RAG-Sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/NitheshK4/RAG-Sentinel/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

<div align="center">
  <img src="frontend/demo-animation.webp" alt="RAG Sentinel Vector space visualizer and ingestion simulator walkthrough animation" width="850" style="border-radius:12px; border: 1px solid rgba(0, 212, 255, 0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />
</div>

## 🎯 What is RAG Poisoning?

Retrieval-Augmented Generation (RAG) systems retrieve documents from a vector index to ground LLM responses in real data. This makes them powerful — and exploitable.

An attacker who can influence what gets indexed can corrupt every downstream answer:

| Attack Class | What It Does |
|---|---|
| **Instruction Injection** | Embeds override commands inside policy documents to redirect LLM behavior |
| **Authority Spoofing** | Claims false institutional authority to push malicious directives into responses |
| **Near-Duplicate Flooding** | Stuffs the index with near-identical poisoned chunks to dominate retrieval rankings |
| **Semantic Drift** | Subtly mutates factual content across a corpus to erode baseline accuracy |
| **Retrieval Bait** | Engineers chunks to rank highly for specific queries and hijack answers |

**RAG Sentinel is the security layer that detects all of these — before and after indexing.**

---

## ✨ Features

### 🔬 9 AI-Powered Detection Pipelines
Each pipeline is a Gemini-backed LLM analysis stage with enforced structured JSON output via Pydantic v2 schemas.

| Pipeline | Endpoint | Purpose |
|---|---|---|
| Source Intake Triage | `POST /api/v1/ingestion/source-triage` | Assess trust signals, provenance, and poisoning risk of a new source before it enters the pipeline |
| Chunk Semantic Audit | `POST /api/v1/ingestion/chunk-audit` | Inspect individual chunks for instruction injection, authority claims, and retrieval bait |
| Neighbor Consistency Audit | `POST /api/v1/detection/neighbor-audit` | Detect spoofed insertions by checking semantic consistency with adjacent chunks |
| Retrieval Trace Investigator | `POST /api/v1/detection/retrieval-trace` | Analyze live retrieval traces for ranking domination and answer corruption |
| Attack Hypothesis Builder | `POST /api/v1/detection/attack-hypothesis` | Synthesize multi-stage evidence into a concise, analyst-verifiable poisoning theory |
| Incident Reporter | `POST /api/v1/reporting/incident-report` | Generate analyst-grade incident reports with confirmed findings and business impact |
| Remediation Planner | `POST /api/v1/reporting/remediation-plan` | Produce prioritized remediation steps balancing containment speed and false-positive risk |
| Attack Generator | `POST /api/v1/evaluation/attack-generator` | Synthesize novel attack payloads for red teaming and benchmark creation |
| Benchmark Judge | `POST /api/v1/evaluation/benchmark-judge` | Score detector output against ground truth to measure detection quality |

### 🖥️ Premium Analyst Console (Single-Page App)
A dark glassmorphism security dashboard served at `http://localhost:8000` with four views:

- **Dashboard** — Live telemetry: Security Health Gauge, Ingestion Traffic Timeline, attack family quick-run cards
- **Pipelines** — Form-driven interface to run any of the 9 AI pipelines, with Load Demo Data support
- **Incidents** — Persistent, real-time feed of investigation results (survives page reloads)
- **Visualizer** — Interactive 2D Embedding Space canvas + Red Team Ingestion Simulator

### 🧪 2D Vector Space Visualizer
An interactive HTML Canvas visualization of vector embeddings in your index:
- **Electric Cyan** = clean policy reference chunks
- **Vibrant Orange** = external/borderline-trust crawler chunks  
- **Glowing Red** = active poisoning payloads
- Click any node to inspect its cosine similarity, centroid distance, source URI, and raw chunk text

### 🔴 Red Team Ingestion Simulator
Step-by-step visual walkthrough of how a chunk traverses the 7-stage security gateway. Load one of three presets and press Simulate:
- `🟢 Clean State` — all stages pass
- `🟠 Authority Spoofing` — blocked at triage
- `🔴 Instruction Injection` — bypasses triage, caught at chunk audit

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG Sentinel                                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Frontend SPA (Vanilla JS + Canvas)                           │   │
│  │  Dashboard · Pipelines · Incidents · Visualizer              │   │
│  └───────────────────────┬──────────────────────────────────────┘   │
│                          │ HTTP / REST                              │
│  ┌───────────────────────▼──────────────────────────────────────┐   │
│  │ FastAPI Backend                                              │   │
│  │                                                              │   │
│  │  Ingestion         Detection           Reporting             │   │
│  │  ├ source-triage   ├ neighbor-audit    ├ incident-report     │   │
│  │  └ chunk-audit     ├ retrieval-trace   └ remediation-plan    │   │
│  │                    └ attack-hypothesis                       │   │
│  │                                                              │   │
│  │  Evaluation        Orchestrator        Demo                  │   │
│  │  ├ attack-gen      └ /orchestrate      ├ /status             │   │
│  │  └ benchmark-judge                     ├ /incidents          │   │
│  │                                        └ /sample-*           │   │
│  │                                                              │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │ Core                                                │    │   │
│  │  │  config.py · prompt_loader.py · llm_client.py       │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └───────────────────────┬──────────────────────────────────────┘   │
│                          │                                          │
│  ┌───────────────────────▼──────────────────────────────────────┐   │
│  │ Gemini 2.0 Flash (via Google AI API)                         │   │
│  │ Graceful fallback: realistic demo JSON when rate-limited     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- A [Google AI API key](https://aistudio.google.com/apikey) (optional — falls back to demo mode automatically)

### 1. Clone
```bash
git clone https://github.com/NitheshK4/RAG-Sentinel.git
cd RAG-Sentinel
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server

**With Gemini API (live inference):**
```bash
GEMINI_API_KEY=your_key_here python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Without API key (demo mode — full UI, realistic mock responses):**
```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Open the dashboard
```
http://localhost:8000
```

Swagger interactive API docs are at `http://localhost:8000/docs`.

### 🐳 Docker

```bash
# Build and run with Docker Compose
docker compose up --build

# Or with a Gemini API key
GEMINI_API_KEY=your_key_here docker compose up --build
```

---

## 📁 Project Structure

```
RAG-Sentinel/
├── backend/
│   ├── core/
│   │   ├── config.py           # Environment + path configuration
│   │   ├── llm_client.py       # Gemini API client with 429 fallback
│   │   └── prompt_loader.py    # In-memory embedded prompt templates
│   ├── models/                 # Pydantic v2 I/O schemas for all 9 pipelines
│   ├── routes/
│   │   ├── ingestion.py        # Source triage + chunk audit endpoints
│   │   ├── detection.py        # Neighbor audit + retrieval trace + hypothesis
│   │   ├── evaluation.py       # Attack generator + benchmark judge
│   │   ├── reporting.py        # Incident reporter + remediation planner
│   │   ├── orchestrator.py     # Single /orchestrate router endpoint
│   │   └── demo.py             # Sample data + persistent incident store
│   └── main.py                 # FastAPI app, CORS, SPA serving, error handlers
├── frontend/
│   ├── index.html              # 5-view SPA with ARIA navigation
│   ├── style.css               # Dark glassmorphism design system
│   └── app.js                  # API calls, canvas visualizer, simulator engine
├── schemas/                    # JSON Schema definitions for all 9 pipeline outputs
├── examples/                   # Realistic sample data bundles for demo loading
└── requirements.txt
```

---

## 🔌 API Reference

All endpoints accept and return `application/json`. The full interactive reference is at `/docs`.

### Ingestion

```http
POST /api/v1/ingestion/source-triage
```
Assess a source before it enters the pipeline. Returns a risk classification, trust tier, and actionable flags.

```http
POST /api/v1/ingestion/chunk-audit
```
Inspect a single chunk for semantic poisoning signals. Returns threat category, confidence score, and evidence summary.

### Detection

```http
POST /api/v1/detection/neighbor-audit
```
Check a chunk against its neighbors for tone shifts, factual contradictions, and spoofed insertions.

```http
POST /api/v1/detection/retrieval-trace
```
Analyze a retrieval trace for ranking domination, query exploitation, and answer corruption.

```http
POST /api/v1/detection/attack-hypothesis
```
Synthesize all prior stage outputs into a single structured poisoning hypothesis.

### Reporting

```http
POST /api/v1/reporting/incident-report
```
Generate a formal analyst incident report with confirmed scope and immediate action items.

```http
POST /api/v1/reporting/remediation-plan
```
Produce a prioritized remediation plan weighted against operational constraints and reindex capability.

### Evaluation

```http
POST /api/v1/evaluation/attack-generator
```
Generate synthetic attack payloads for red team exercises and benchmark dataset creation.

```http
POST /api/v1/evaluation/benchmark-judge
```
Score detector output against ground truth labels and return precision/recall metrics.

### Health & Demo

```http
GET  /api/v1/health                        → { status, version, demo_mode }
GET  /api/v1/health/ready                  → Readiness probe with dependency checks
GET  /api/v1/system/info                   → Runtime and config metadata
GET  /api/v1/demo/incidents                → Persistent in-memory incident log
POST /api/v1/demo/incidents                → Append incident to persistent store
GET  /api/v1/demo/incidents/{index}        → Single incident detail by index
POST /api/v1/demo/incidents/{index}/notes  → Add analyst note to an incident
GET  /api/v1/demo/sample-source-bundle     → Pre-built demo input bundle
GET  /api/v1/demo/sample-incident-report   → Pre-built demo incident report
```

### Health & Operations

Detailed diagnostics and operational monitoring endpoints:

* **`GET /api/v1/health`**: Returns basic operational state (`"status": "ok"`), app version, and whether demo mode is active.
* **`GET /api/v1/health/ready`**: A dependency-aware readiness probe that validates LLM API connectivity (if not in demo mode), memory stores for settings, and incident history. Returns HTTP `200 OK` on success, or HTTP `503 Service Unavailable` if any check fails.
* **`GET /api/v1/system/info`**: Exposes system operational metadata including Python version, platform architecture, dependency library versions (FastAPI, Pydantic), and total registered API routes.

---

## 🛡️ Design Principles

- **Every pipeline has a single responsibility.** No prompt does more than one job.
- **Every output is machine-parseable.** Pydantic v2 enforces the contract at the API boundary.
- **No silent failures.** The LLM client catches rate limit errors (HTTP 429) and falls back to high-fidelity demo JSON. No blank screens, no 500s in production.
- **Prompts are not stored on disk.** All 10 prompt templates are embedded in memory in `prompt_loader.py`. The system is fully self-contained — clone and run.
- **Concurrency is safe.** The in-memory incident store is protected by `threading.Lock()`.
- **Human review is required.** The system flags `high` and `critical` severity findings but never takes destructive remediation action automatically.

---

## ⚙️ Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Google AI API key. If empty, the system runs in demo mode. |
| `RATE_LIMIT_RPM` | `120` | Max requests per minute per IP. |
| `RATE_LIMIT_BURST` | `20` | Burst allowance above RPM limit. |

Demo mode returns realistic, analyst-grade mock responses for all 9 pipelines — fully usable for evaluation, demos, and local development without spending API quota.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI 0.111, Uvicorn |
| Validation | Pydantic v2 |
| LLM | Google Gemini 2.0 Flash via `httpx` |
| Frontend | Vanilla JS, HTML5 Canvas, CSS Glassmorphism |
| Prompt engine | In-memory embedded templates with `{{variable}}` interpolation |

---

## 📜 License

MIT — see [LICENSE](LICENSE).

---

## 🔧 Troubleshooting

### Rate Limiting Errors (HTTP 429)
If you encounter `HTTP 429 Rate Limit Exceeded` during intense API operations, it is likely due to the sliding-window IP rate limiter. You can raise or adjust this limit in local development by configuring environment variables:
```bash
RATE_LIMIT_RPM=500 RATE_LIMIT_BURST=100 python3 -m uvicorn backend.main:app --reload
```

### Static Asset Serving & Caching
The backend app serves static SPA assets. If changes to the frontend do not load immediately in your browser:
* Verify that your browser caching is disabled in developer tools.
* The API serving routes return `Cache-Control: no-cache` for HTML requests, but browser memory cache might still interfere. Perform a hard reload (`Cmd+Shift+R` or `Ctrl+F5`).

### LLM Connectivity Failures
When running in Live Mode, if `/api/v1/health/ready` reports the `llm_api` check as `degraded`:
* Verify your `GEMINI_API_KEY` environment variable is correctly set and exported.
* Ensure your machine has outbound access to `generativelanguage.googleapis.com`.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR guidelines.

---

<div align="center">

Built to make RAG systems harder to poison. 🛡️

</div>

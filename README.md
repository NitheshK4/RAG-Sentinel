# Antigravity Prompt Package: Vector Index Poisoning Detector

## Purpose

This package is a production-ready prompt and documentation system for a `Vector Index Poisoning Detector`: a security-focused AI pipeline that identifies malicious, manipulative, or retrieval-dominating chunks before and after they enter a RAG index.

The package is designed to be handed directly to Antigravity as an operational prompt folder. It assumes Antigravity can ingest prompt specifications from Markdown files and enforce structured outputs from the JSON schemas included in this package.

## Outcome

With this folder, an implementation team can:

- classify incoming sources and chunks for poisoning risk
- investigate suspicious retrieval behavior
- generate synthetic poisoning attacks for benchmark creation
- produce analyst-grade incident reports and remediation plans
- extend the prompt system without breaking formatting or output contracts

## Package Map

- [docs/architecture.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/architecture.md)
- [docs/dataset-plan.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/dataset-plan.md)
- [docs/tech-stack.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/tech-stack.md)
- [docs/folder-structure.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/folder-structure.md)
- [docs/implementation-guidelines.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/implementation-guidelines.md)
- [docs/operations-and-troubleshooting.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/operations-and-troubleshooting.md)
- [docs/future-expansion.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/docs/future-expansion.md)
- [prompts/PROMPT_INDEX.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/prompts/PROMPT_INDEX.md)
- [governance/versioning-policy.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/governance/versioning-policy.md)
- [governance/qa-checklist.md](/Users/nitheshkumar/Documents/New%20project/antigravity-vector-index-poisoning-detector/governance/qa-checklist.md)

## Prompt System Design Principles

- Every prompt must produce machine-parseable output.
- Every prompt must have a single clear responsibility.
- Every prompt must declare its assumptions and abstain on missing evidence.
- Every prompt must prefer evidence-backed risk reasoning over generic “AI security” language.
- Every prompt must be resilient to prompt injection attempts present inside inspected documents.

## Recommended Runtime Policy

- Default temperature: `0.0` to `0.2`
- Structured output required for all pipeline-critical prompts
- Prompt templates treated as versioned assets
- Runtime guardrail: never allow inspected document text to modify system instructions
- Human review required for `high` severity incidents before destructive remediation

## Expected End-to-End Flow

1. Run source intake triage on each newly discovered source.
2. Run chunk semantic audit during chunking and pre-index review.
3. Run neighbor consistency audit against source-local and corpus-local context.
4. Monitor retrieval traces in production for unusual dominance or instruction takeover.
5. Use the attack hypothesis builder to consolidate evidence into a poisoning theory.
6. Produce a formal incident report and remediation plan.
7. Use the benchmark prompts to generate attack sets and score detector quality.

## Handoff Checklist

- Confirm Antigravity supports Markdown-based prompt definitions.
- Map each prompt file to a runtime route or job name.
- Enforce the corresponding schema under `schemas/` at execution time.
- Store every prompt invocation, raw input bundle, and structured output for auditability.
- Run the QA checklist before releasing prompt changes.

## Assumptions

- Antigravity is the prompt execution and orchestration environment.
- The implementation team will connect these prompts to a Python or TypeScript service.
- The project uses a hybrid detection strategy: heuristics, embeddings, retrieval telemetry, and LLM semantic analysis.


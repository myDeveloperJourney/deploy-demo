# Multi-Agent Chat Demo

A small FastAPI chat interface for **testing how a language model behaves when it is wrapped in an agentic framework** — i.e. when the model can route to specialized tools instead of answering everything itself. Built to make the difference between a raw LLM call and an orchestrated multi-agent system concrete and observable.

## What it does

You type a question into a single chat box. A lightweight router inspects the request and dispatches it to the right specialized agent, then returns the result:

| Agent | Handles | Notes |
|---|---|---|
| **Math agent** | Arithmetic / calculation prompts | 5-tool ReAct agent |
| **SQL agent** | Questions about the sample database | Read-only, guardrailed (see below) |
| **Search agent** | Open-web lookups | DuckDuckGo-backed |
| **Orchestrator** | Routing | Deterministic keyword router |

The point is to *watch* model behavior change across these paths — how it reasons, where it succeeds, and where guardrails have to catch it.

## Engineering notes (the interesting parts)

- **Guardrailed SQL.** The SQL agent rejects destructive statements (`DROP`/`DELETE`/etc.) and auto-applies `LIMIT 100`, so a model that "decides" to run something dangerous is stopped at the boundary. This is the demo's main lesson: the unguarded model is a liability; the guard is the engineering.
- **Deterministic routing** over an LLM-router so behavior is reproducible while testing.
- **Deployable.** Ships with a `Procfile` and `railway.json` (healthcheck included) so it runs on a public URL, not just localhost.

## Stack
Python · FastAPI · a ReAct agent pattern · SQLite (sample DB) · Railway-ready.

## Run it locally

```bash
pip install -r requirements.txt
python create_sample_db.py        # builds data/sample.db (customers/products/orders)
uvicorn main:app --reload         # open http://127.0.0.1:8000
```

Copy `.env.example` to `.env` and add your keys first.

---

*Authored by Daniel J. Scott. A personal sandbox for exploring agentic LLM patterns and the production guardrails real deployments need.*

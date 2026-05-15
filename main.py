"""FastAPI wrapper around the Lab 4.4 multi-agent workflow.

This is the Day 5 deployment demo. It exposes the same three agents
(Math / SQL / Search) plus the AgentWorkflow router as a public HTTP
endpoint, with a simple HTML form for the demo.

The verbose ReAct traces from LangChain are written to stdout, which
Railway captures and surfaces in its dashboard. That's intentional —
showing those live logs IS the Operations-pillar demo moment.
"""
import logging
import os
import time

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agents.workflow import AgentWorkflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("multiagent")

if not os.getenv("OPENAI_API_KEY"):
    log.warning("OPENAI_API_KEY is not set — agent calls will fail.")

app = FastAPI(title="Deloitte × GA — Multi-Agent Demo")
templates = Jinja2Templates(directory="templates")

# One workflow instance, shared across requests.
workflow = AgentWorkflow(db_path="data/sample.db")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": None, "question": "", "task_type": "auto", "elapsed": None},
    )


@app.post("/query", response_class=HTMLResponse)
async def query(
    request: Request,
    question: str = Form(...),
    task_type: str = Form("auto"),
):
    start = time.time()
    log.info("Query received: type=%r question=%r", task_type, question)
    try:
        result = workflow.run(question, task_type=task_type)
        log.info("Query succeeded in %.2fs", time.time() - start)
    except Exception as exc:  # noqa: BLE001 — show the error to the student
        log.exception("Query failed")
        result = f"Error: {exc}"
    elapsed = f"{time.time() - start:.2f}s"
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "question": question,
            "task_type": task_type,
            "elapsed": elapsed,
        },
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

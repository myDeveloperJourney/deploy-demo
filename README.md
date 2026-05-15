# Multi-Agent Deployment Demo

Day 5 demo asset for the Deloitte × General Assembly *Gen AI Frameworks & Tools* course.

This is the Lab 4.4 multi-agent workflow (Math + SQL + Search + Orchestrator) wrapped in a FastAPI app, ready to deploy to Railway. The purpose is to make the **demo trap → production** story concrete: students see the same code they wrote locally running on a public URL.

## What's included

```
deploy-demo/
├── main.py                    FastAPI app — / form, /query endpoint, /healthz
├── agents/
│   ├── math_agent.py          5-tool arithmetic ReAct agent (same as Lab 4.4)
│   ├── sql_agent.py           SQL agent + read-only guardrails (rejects DROP/DELETE/etc, auto-LIMIT 100)
│   ├── search_agent.py        DuckDuckGo search agent
│   └── workflow.py            Deterministic keyword-based router
├── templates/
│   └── index.html             Single-page form for the demo
├── create_sample_db.py        Builds data/sample.db with customers/products/orders
├── requirements.txt
├── Procfile                   Railway/Heroku-compatible
├── railway.json               Railway build config + healthcheck
├── .gitignore
├── .env.example
└── README.md                  (this file)
```

## Production differences from Lab 4.4 (talk through these in class)

The lab code is intentionally unguarded — that's the teaching point. This deployment adds the production layer:

| Concern | Lab 4.4 | This deployment |
|---|---|---|
| SQL injection / destructive queries | None | Regex rejects DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE/CREATE/ATTACH/DETACH/PRAGMA |
| Unbounded result sets | None | Auto-injects `LIMIT 100` if missing |
| Agent error handling | Crashes worker | Try/except wraps every query; surfaces error to user |
| Observability | print() to terminal | Structured logging to stdout → Railway dashboard |
| Health check | None | `/healthz` for Railway's load balancer |
| Iteration limits | None | `max_iterations=5` on every agent (prevents runaway loops) |
| Secret management | `.env` file on local disk | Railway env var, never committed |

That side-by-side IS the production-pillar conversation in slide form.

---

## Deploy to Railway (the live class flow)

### Step 1 — Local smoke test (5 min, optional but recommended)

```bash
cd deploy-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python create_sample_db.py
cp .env.example .env
# Edit .env and put your real OPENAI_API_KEY in
export $(cat .env | xargs)
uvicorn main:app --reload --port 8000
```

Hit http://127.0.0.1:8000 in a browser, run one of the example queries. If that works, the deploy will work.

### Step 2 — Push to a new GitHub repo

```bash
cd deploy-demo
git init
git add .
git commit -m "Initial commit: multi-agent demo for Day 5"
# Create a new empty repo on github.com (e.g. deloitte-multiagent-demo, can be private)
git remote add origin https://github.com/YOUR_USERNAME/deloitte-multiagent-demo.git
git branch -M main
git push -u origin main
```

### Step 3 — Deploy on Railway (10 min)

1. Go to https://railway.app and sign in (GitHub auth is fastest).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Authorize Railway to access the repo if prompted, then pick `deloitte-multiagent-demo`.
4. Railway will auto-detect Python (via `requirements.txt`) and start building. The first build takes ~3 minutes.
5. While it's building, go to the **Variables** tab and add:
   - `OPENAI_API_KEY` = your real OpenAI key
6. Go to the **Settings** tab → **Networking** → click **Generate Domain**. Railway gives you a `*.up.railway.app` URL.
7. Wait for the deploy status to flip to green ("Active"). The first deploy after adding the env var triggers a rebuild — give it another minute.
8. Open the URL in a browser. The form should load.

### Step 4 — Smoke-test the deployment

Run each of these once before class to make sure the path works AND to warm the worker (cold starts add ~5 seconds):

| Question | Expected agent | Expected behavior |
|---|---|---|
| `What is 45 times 12?` | Math | Returns `540` |
| `What is the square root of 144 plus 5?` | Math | Returns `17` (two tool calls) |
| `How many customers are in the North America region?` | SQL | Returns `5` |
| `List the top 3 customers by total order value` | SQL | Returns a table |
| `What's the latest news on Claude AI?` | Search | Returns a summary from web results |

### Step 5 — Wire up the demo moment

For the live class:

1. **Have the Railway URL and the Railway logs view open in two tabs.** Pre-warm by running one query 5 minutes before class.
2. **Run a query through the UI.** Show the Final Answer.
3. **Flip to the Railway logs tab.** The verbose ReAct trace from the agent (Thought → Action → Observation) is right there in production logs. *This* is the moment that makes the Operations pillar concrete — same trace they saw locally yesterday, now running on a public server.
4. **Run the same query with task_type forced to a different agent.** Show that the routing works.
5. **Show one query failing gracefully** (try `What is 0 divided by 0?` or `DROP TABLE customers`). Point out: the guardrail message is what production looks like.

---

## Cost & safety notes

- **Token cost per query**: GPT-4o-mini at current pricing, a typical 2-step ReAct query costs about $0.001–0.003. A full class of 20 students each running 3 queries is roughly $0.10. Don't worry about it.
- **Free tier**: Railway gives $5 of usage per month on the trial plan — that covers this demo many times over.
- **Sharing the URL**: Safe to share with the class. The SQL guardrails block destructive queries. The DB resets on every redeploy. There's no auth, so don't post the URL publicly long-term — once class is over, either delete the Railway project or add basic auth.
- **Your API key**: never commit `.env`. The `.gitignore` already excludes it.

## Troubleshooting

**Build fails on Railway with `ModuleNotFoundError`**
The dependency pinning in `requirements.txt` is conservative but if Railway is using a newer Python version that breaks something, set the Python version explicitly: add a file called `runtime.txt` with `python-3.11` in it.

**`/healthz` returns 503**
The app is still booting. Wait 30 seconds. If it persists, check the **Deployments** → **Logs** tab in Railway — there's almost certainly a Python traceback explaining why.

**Search agent fails with rate limit**
DuckDuckGo will occasionally rate-limit a noisy IP. Wait 60 seconds and retry, or use the task_type override to route to Math or SQL.

**Cold start takes too long during the demo**
Run a warmup query 5 minutes before class. Railway's free tier sleeps the app after ~10 min of inactivity.

**You want to disable the URL after class**
Railway → Project → Settings → Delete project. Or just remove the public domain under Networking. The OpenAI key never leaves your env vars.

---

## Where this fits in the Day 5 narrative

This deployment is the artifact that anchors the second half of Day 5:

- **Slide 21 — The Demo Trap**: "Works on one developer's machine ✓" — and yet here it is running on a public URL. The boxes you couldn't tick locally (24/7, real traffic, monitoring) are now visible in Railway's dashboard.
- **Slide 22 — The Five Production Pillars**: Scaling (Railway autoscales), Security (env-var key, SQL guardrails), Integration (FastAPI endpoint anyone can hit), Operations (logs, healthcheck, restart policy), Adoption (the form UI).
- **Slide 23 — Where to Deploy**: Railway is one of the three named platforms. Walking the talk.
- **Slide 20 — Guardrails Design Checkpoint**: The SQL agent answers every question on the checklist — input validated, tool gated, output bounded, runtime monitored.

The whole point of building this was to make those slides true rather than theoretical. Have fun.

# Job Fit Agent (v2)

An agentic job-posting triage tool. Given a job URL, it decides whether the role is worth applying to — returning `apply`, `borderline`, or `skip` with structured reasoning.

Built as a portfolio project to demonstrate agent design: tool definition, orchestration via tool descriptions, and evaluation against manual ground truth.

## What it does

1. Fetches a job posting from a URL
2. Extracts triage-relevant signals (title, company, location, languages, seniority)
3. Applies hard filters (language match + LLM-judged seniority fit)
4. If filters pass, assesses overall fit against the candidate profile
5. Returns a structured verdict with confidence + strengths + gaps

The agent decides the tool sequence itself — it skips extraction on dead postings, short-circuits on failed filters, and returns early when a decision is clear.

## Architecture

Standard OpenAI tool-calling loop. Max 8 iterations. No framework (no LangChain etc.) — pure Python + OpenAI SDK.

Five tools:
- `fetch_job_posting` — HTTP fetch + HTML cleanup
- `extract_job_signals` — LLM-based extraction of triage fields
- `check_hard_filters` — deterministic language check + LLM seniority judgment
- `assess_fit` — LLM-based soft judgment with structured output
- `search_company_context` — deferred (v2.1)

See `DESIGN.md` for full design rationale.

## Stack

Python, FastAPI, OpenAI API (tool use + JSON mode), vanilla JS frontend.

## How to run

```bash
pip install fastapi uvicorn openai python-dotenv requests beautifulsoup4
echo "OPENAI_API_KEY=sk-..." > .env
uvicorn backend:app --reload
```

Then open `http://localhost:8000`.

CLI usage:
```bash
python agent.py "https://example.com/job-posting"
```

Evaluation:
```bash
python eval_runner.py
```

## Project structure

- `agent.py` — main agent loop + tool definitions
- `skills/` — individual tool implementations
- `data/profile.json` — candidate profile (hard filters + soft signals)
- `data/eval_set.csv` — ground-truth verdicts for evaluation
- `eval_runner.py` — runs the agent across the eval set and reports agreement
- `backend.py` — FastAPI server
- `index.html` — web UI (v1, v2 UI planned)

## Evaluation

The agent is evaluated against a manually-scored eval set. Agreement between the agent's verdicts and my manual scoring is tracked as the primary quality metric.

Current state: 80% agreement on fetchable URLs (v2 alpha, small eval set).

## Known limitations

- Some sites (Workday, LinkedIn, some careers portals) block automated fetching. The UI supports pasting job text manually for these cases.
- v2 uses training-knowledge-based company context with an eval-triggered upgrade path to web search.

## What's next

- Web UI for v2 (`/analyze/v2`) with manual-paste fallback for blocked URLs
- Expand eval set to 15+ URLs
- CV recommendation tool for `apply` verdicts
- Optional web search for borderline cases
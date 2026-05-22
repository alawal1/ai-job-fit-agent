# Job Fit Agent (v2)

An agentic job-posting tool. Given a job URL, it decides whether the role is worth applying to — returning `apply`, `borderline`, or `skip` with structured reasoning.

Built as a portfolio project to demonstrate agent design: tool definition, orchestration via tool descriptions, and evaluation against manual ground truth.

## What it does

1. Fetches a job posting from a URL
2. Extracts triage-relevant signals (title, company, location, languages, seniority)
3. Applies hard filters (language match + LLM-judged seniority fit)
4. If filters pass, assesses overall fit against the candidate profile
5. Returns: verdict (apply/borderline/skip), confidence (high/medium/low) strengths, gaps

The agent decides the tool sequence itself — it skips extraction on dead postings, short-circuits on failed filters, and returns early when a decision is clear.

## Architecture

Standard OpenAI tool-calling loop. Max 8 iterations. No framework (no LangChain etc.) — pure Python + OpenAI SDK.

**Four tools:**
- `fetch_job_posting` — HTTP fetch + HTML cleanup
- `extract_job_signals` — LLM extraction of triage-relevant fields
- `check_hard_filters` — deterministic language check + LLM seniority judgment
- `assess_fit` — LLM soft judgment, returns structured verdict + reasoning


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

```
v2/
├── agent.py              # Main loop + tool definitions
├── backend.py            # FastAPI server
├── index.html            # Web UI
├── skills/               # Tool implementations
│   ├── fetch_job.py
│   ├── extract_signals.py
│   ├── check_filters.py
│   └── assess_fit.py
├── data/
│   ├── profile.json      # Candidate profile (hard filters + soft signals)
│   └── eval_set.csv      # Ground-truth verdicts for evaluation
└── eval_runner.py        # Eval against manual scoring
```

## Evaluation

Agent evaluated against manually-scored job postings. Primary metric: agreement with my triage decisions.

**Current:** 80% agreement on 5 fetchable URLs (small eval set, v2 alpha).

Disagreements traced to profile miscalibration (overly optimistic manual scoring vs. stated hard filters). Agent held to stricter-but-principled verdicts.

## Known limitations

- Workday, LinkedIn, some careers portals block automated fetching → UI supports manual paste fallback
- Company context uses training knowledge (no web search) with eval-triggered upgrade path planned

## What's next (v2.1)

- CV recommendation tool for `apply` verdicts
- SQLite for cross-analysis history
- Expand eval set to 15+ URLs
- Web search for borderline company context
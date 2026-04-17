# Job Fit Agent

A web-enabled Python project that analyzes job postings against a candidate profile and presents fit recommendations through a clean interface.

## What it does
- Loads candidate profile data from local markdown files in `data/`
- Fetches job posting content from a provided URL
- Uses OpenAI tool use to evaluate fit and return structured output
- Produces fit score, decision, matches, gaps, reasoning, and CV recommendations
- Serves a web UI for pasting job URLs and viewing results immediately

## How to run
From the project root:
```bash
uvicorn backend:app --reload
```
Then open:

`http://localhost:8000`

## Stack
- Python
- FastAPI
- OpenAI API with tool use
- vanilla JavaScript frontend

## Project structure
- `agent.py` — OpenAI integration, tool definitions, job posting fetcher, profile loader
- `batch.py` — batch processing helper for bulk job analysis
- `backend.py` — FastAPI backend exposing `/analyze` and serving `index.html`
- `index.html` — self-contained frontend UI
- `data/` — candidate profile and job URL source files

## Known limitations
- LinkedIn URLs and some protected career sites may block scraping or return unusable HTML
- Results depend on scraper success and can fail if page structure changes or content is restricted
- CV recommendations should be reviewed manually before use
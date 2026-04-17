# Job Fit Agent

A Python agent that analyzes job postings and evaluates candidate fit using an agentic loop with tool use.

## What it does
- Fetches job postings directly from URLs
- Loads a structured candidate profile from local markdown files
- Reasons about fit using OpenAI tool use — the model decides what to check, not hardcoded steps
- Returns a structured verdict: fit score, matches, gaps, CV recommendations
- Batch processes multiple URLs and saves results to Excel automatically
- Skips roles below 70% fit and detects duplicates

## How to run

Add job URLs to `data/jobs/urls.txt`, one per line:
```
https://company.com/job-posting
```

Then run:
```bash
python batch.py
```

Results are saved to `outputs/` as markdown reports and to `tracker.xlsx`.

## Project structure
- `agent.py` — agentic loop, tool definitions, OpenAI integration
- `batch.py` — batch runner, Excel tracker, duplicate detection
- `data/` — candidate profile files (skills, experience, education, projects)
- `outputs/` — per-job markdown reports

## Stack
Python, OpenAI API (tool use), openpyxl, BeautifulSoup

## Known limitations
- CV rewriting tends to hallucinate actions not present in the original bullets. Use suggestions as inspiration only, not verbatim.
- LinkedIn URLs and some career sites block scraping and return no data.
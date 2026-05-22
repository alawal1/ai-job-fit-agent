# Job Fit Agent

A polished landing page for a job-fit evaluation assistant designed to make hiring decisions easier and show the work behind every application.

This repository contains a candidate-driven agent that reads job postings, compares them with a candidate profile, and produces structured recommendations for fit, shortlisting, and CV improvements.

## Why this repo matters
- Provides a clear, data-driven view of how a candidate matches a role
- Converts job descriptions into fit scores, role matches, and gap analysis
- Generates candidate-facing suggestions for CV and profile updates
- Helps hiring managers quickly understand why a candidate is a strong fit

## What you will find here
- A main top-level implementation for quick batch evaluation and reporting
- `v1/` for the first prototype and earlier experimental tooling
- `v2/` for the current advanced version with richer analysis, filters, and improved fit signals

## Branches / versions explained
- `main` / root folder: the current repo landing page and core evaluation entrypoint.
  - Best for sharing as a GitHub link with a hiring manager.
  - Contains the high-level project overview, batch runner, and profile data model.
- `v1/`: the initial agent prototype.
  - Early job-fetching, profile loading, and basic fit reasoning.
  - Useful for understanding the first design and how the tool started.
- `v2/`: the improved production-ready workflow.
  - Better signal extraction, fit assessment, filter checking, and CV recommendation features.
  - Includes a dashboard-style interface and more structured outputs.

## How to explore the repo
1. Read this `README.md` as the project landing page.
2. Review the candidate profile files under `data/` for skills, experience, education, projects, and positioning.
3. Compare the implementation in `v1/` and `v2/` to see the evolution of the agent.
4. Use `batch.py` at the root for the current batch processing flow.

## How to run the current version
Add job URLs to `data/jobs/urls.txt`, one per line:

```text
https://company.com/job-posting
```

Then run:

```bash
python batch.py
```

This creates evaluation results in `outputs/` and updates the tracker file with job fit details.

## Key files at the root
- `agent.py` — core agent loop, tool definitions, OpenAI integration
- `batch.py` — batch job runner, duplicate detection, and report generation
- `data/` — candidate profile and job URL source data
- `outputs/` — generated fit reports for each analyzed job

## Why send this link to a hiring manager
- It shows the candidate’s process, not just a resume.
- It explains how job fit is measured, with transparent outputs.
- It highlights the project’s structure and the matured version history.

## Stack
Python, OpenAI API, openpyxl, BeautifulSoup
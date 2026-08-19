# Job Triage Agent — Design Overview

## Goal
Triage agent: decides apply / borderline / skip for job postings.

## Architecture
Standard OpenAI tool-calling loop. Max 8 iterations.
5 tools, agent chooses sequence:
- fetch_job_posting — existing
- extract_job_signals — LLM extraction
- check_hard_filters — hybrid (deterministic languages + LLM seniority)
- assess_fit — LLM judgment, returns verdict + confidence + structured reasoning
- search_company_context — LLM-only, called only on borderline cases

## Key design principles
- Tool descriptions encode orchestration (when to call, when NOT to call)
- Deterministic where rules are clear, LLM where language understanding matters
- State flows through tools as structured data, not agent memory
- `borderline` verdict must carry open_questions (prevents hedging)

## Debugging log
Four bug categories hit during v2 build:
1. Shell backgrounding URLs with `&` → always quote URLs
2. Agent skipping tool → system prompt too loose, tightened to required workflow
3. Silent exception swallower in _execute_tool wrapper → added [TOOL ERROR] logging
4. Unescaped `{...}` in prompt template broke .format() → switched to string concat

## Known limitations

- **Workday and LinkedIn URLs cannot be fetched programmatically.** These sites render job content via JavaScript and block simple HTTP fetching. `fetch_job_posting` returns empty text for these URLs, and the agent correctly defaults to skip on empty input. Planned workaround (UI phase): detect these URL patterns client-side, prompt the user to paste the job description directly, and feed the text straight into `extract_job_signals`, bypassing `fetch_job_posting`.
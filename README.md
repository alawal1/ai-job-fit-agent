# Job Application Agent

**Status:** Work in progress (v2.1) — core features working, expanding evaluation set

An AI tool that reads job postings and tells you: **apply**, **maybe**, or **skip**. For strong matches, it suggests how to improve your CV for that specific job.

Built to show: tool-calling with LLMs, mixing rule-based + AI logic, testing against real decisions, and iterative development with git branches.

---

## What it does

**The flow:**
1. Gets the job posting (paste manually if the site blocks automated access)
2. Pulls out key info: title, company, location, language requirements, experience level
3. Checks deal-breakers: Do you speak the required languages? Does the seniority level match?
4. If it passes, evaluates overall fit: what matches, what doesn't, how confident is the assessment
5. **New in v2.1:** For jobs worth applying to, suggests specific CV improvements

**How it's designed:**
- Uses simple rules where possible (language matching), AI only when human judgment is needed (seniority level)
- Stops early on dead postings or failed requirements (doesn't waste API calls)
- Tools know when to call each other through clear instructions, not hardcoded sequences

---

## Stack

Python • FastAPI • OpenAI API (function calling) • Plain JavaScript

No frameworks like LangChain — built from scratch to understand how agents actually work.

---

## Quick start

```bash
pip install fastapi uvicorn openai python-dotenv requests beautifulsoup4
echo "OPENAI_API_KEY=sk-..." > .env

# Web interface
uvicorn backend:app --reload
# → http://localhost:8000

# Command line — single job
python agent.py "https://example.com/job"
```

### Batch mode (2–10 URLs)

Paste multiple job URLs into the web interface and they'll be analysed in parallel. Results are ranked by fit score so the best matches appear first.

```bash
# Or via the API directly
curl -X POST http://localhost:8000/analyze/v2/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/job1", "https://example.com/job2"]}'
```

---

## Testing

I tested the agent against jobs I manually scored myself.

**Current:** 80% agreement on 5 working URLs (small test set so far)

The disagreements were interesting: the agent was stricter than my manual scoring. When I said "I'd apply anyway," the agent correctly said "this fails your stated requirements." Kept the agent's stricter logic.

---

## File structure

```
v2/
├── agent.py              # Main loop + tool setup
├── backend.py            # Web server
├── index.html            # UI
├── skills/               # Each tool (fetch, extract, check, assess, suggest)
├── data/
│   ├── profile.json      # My requirements (languages, seniority)
│   ├── profile/          # Detailed background for the AI
│   └── eval_set.csv      # Test cases with expected answers
└── DESIGN.md             # Why I built it this way + debugging notes
```

---

## Current limitations

- **Some sites block automated access:** LinkedIn, Workday, others — you paste the text manually instead
- **Company research uses training data only:** No live web search yet (planned upgrade)

---

## Next steps (v2.2+)

- [ ] Test on 15+ jobs across different industries
- [ ] Save history to database to spot patterns across applications
- [ ] Add web search for companies I don't know
- [ ] Deploy somewhere (runs locally now)

---

## Why this project

I built this to show I can:
- Design tools that work together without hardcoding every step
- Mix simple rules with AI where each makes sense
- Test against real data and learn from the gaps
- Use git properly (built CV feature on a branch, merged when working)
- Ship in small pieces instead of trying to build everything at once

Made for junior data/AI consultant job applications. Check commit history to see how it evolved.
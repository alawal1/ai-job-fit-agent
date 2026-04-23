# Job Fit Agent - Developer Guide

A Python/FastAPI agent that analyzes job postings against a candidate profile using OpenAI's tool use capabilities.

## Quick Start

**Run the web server:**
```bash
uvicorn backend:app --reload
```
Then open `http://localhost:8000`

**Environment setup:**
- Create `.env` file with `OPENAI_API_KEY=sk-...`
- Install dependencies: `pip install fastapi uvicorn openai python-dotenv requests beautifulsoup4`

## Architecture

### Core Flow
1. User pastes job URL in web UI (`index.html`)
2. Frontend POSTs to `/analyze` endpoint (`backend.py`)
3. `agent.py` runs OpenAI agentic loop using tool definitions
4. Tools fetch job content and load candidate profile from `data/` markdown files
5. OpenAI returns structured JSON analysis
6. Frontend displays results

### Key Files

| File | Purpose |
|------|---------|
| `agent.py` | OpenAI integration, tool definitions, agentic loop |
| `backend.py` | FastAPI endpoints (`/analyze`, `/profile`, root HTML) |
| `skills/fetch_job.py` | Network utility: downloads & cleans HTML from URL |
| `skills/load_profile.py` | Reads candidate profile markdown files from `data/` |
| `index.html` | Self-contained frontend with vanilla JS |
| `data/*.md` | Candidate profile markdown files (cv, skills, experience, etc.) |
| `outputs/*.md` | Example analysis results for reference |

## Development Patterns

### Tool Definition Pattern
OpenAI tool definitions live in `agent.py`:
- Each tool needs `TOOL_DEFINITIONS` list entry with name/description/parameters
- Corresponding implementation in `TOOLS` dict maps to actual Python function
- Tools must be pure functions (no side effects on global state)

```python
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_job_posting",
            "description": "Fetches job posting text from URL",
            "parameters": {"type": "object", "properties": {...}}
        }
    }
]
TOOLS = {"fetch_job_posting": fetch_job_posting}
```

### Skills Module Convention
- Each skill in `skills/` is a standalone utility module
- Must include docstrings with `Args`, `Returns`, `Raises` sections
- Handle errors gracefully (NetworkException, FileNotFoundError, etc.)
- Keep functions focused and reusable

### Data Structure: Candidate Profile
Profile data lives in `data/` as markdown files:
- `cv.md` - Formal CV (not included in profile)
- `skills.md`, `experience.md`, `education.md`, `projects.md`, `positioning.md` - Combined by `load_full_profile()`
- `jobs/urls.txt` - URLs for batch processing

### Analysis JSON Output Structure
The agent returns this JSON format (see `outputs/` for examples):

```json
{
    "company": "Company Name",
    "role": "Job Title",
    "fit_score": 75,
    "decision": "APPLY | PASS | REVISIT",
    "matches": ["Keyword 1", "Keyword 2"],
    "gaps": ["Missing skill"],
    "reasoning": "Detailed explanation",
    "cv_recommendations": {
        "add": "Skills to add to CV",
        "remove": "Sections to remove"
    }
}
```

### Important Agent Rules (in system prompt)
- Always call `fetch_job_posting` before reasoning
- Always call `load_full_profile` for candidate data
- Never guess or invent information
- Match/gap keywords must be 2-3 words max, not full sentences
- CV recommendations are specific to each role

## Common Tasks

### Adding a New Analysis Tool
1. Create function in `skills/new_tool.py` with docstrings
2. Import in `agent.py`
3. Add to `TOOL_DEFINITIONS` with proper schema
4. Add mapping to `TOOLS` dict

### Modifying Analysis Logic
- System prompt is in `run_agent()` function in `agent.py`
- JSON schema constraints are in the system prompt
- Output parsing happens in `parse_result()` function

### Updating Candidate Profile
- Edit markdown files in `data/`
- Run agent - it automatically loads from `data/` directory
- `load_full_profile()` excludes `cv.md` intentionally

### Batch Processing
- Use `batch.py` script with job URLs
- Outputs analysis results to `outputs/` directory

## Known Limitations & Edge Cases
- Some sites (LinkedIn, protected pages) block scraping
- Results depend on page structure - may fail if page layout changes
- Timeouts set to 10 seconds for network requests
- HTML cleaning removes script/style/nav/footer tags
- Content truncated to 6000 characters for token efficiency

## Frontend Notes
- `index.html` is self-contained (all CSS/JS inline)
- Communicates with backend via `POST /analyze` and `GET /profile`
- Results rendered as markdown in the UI
- No build process required

## Error Handling Patterns
- Network errors: Catch in `fetch_job.py`, raise RuntimeError with context
- File errors: Catch in `load_profile.py`, skip missing files gracefully
- OpenAI errors: Let bubble up from `run_agent()` - caught in FastAPI route
- JSON parse errors: Handled in `parse_result()` with fallback response

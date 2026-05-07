# backend.py
import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from agent import run_agent_v2, run_agent_v2_from_text

app = FastAPI()

BLOCKED_DOMAINS = ["linkedin.com", "workday.com", "myworkdayjobs.com"]


def is_blocked_url(url: str) -> bool:
    return any(d in url.lower() for d in BLOCKED_DOMAINS)


@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse("index.html")


@app.post("/analyze/v2")
async def analyze_v2(request: Request):
    payload = await request.json()
    url = payload.get("url")
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=400, detail={"error": "A valid 'url' field is required."})

    url = url.strip()
    if is_blocked_url(url):
        return JSONResponse(content={"blocked": True, "message": "This site blocks automated fetching. Please paste the job description manually."})

    try:
        result = run_agent_v2(url)
        print(f"[BACKEND] Returning: {json.dumps(result, indent=2)}", flush=True)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})

    if result.get("tool_calls_made", 0) == 1 and "empty" in (result.get("final_message") or "").lower():
        return JSONResponse(content={"blocked": True, "message": "Could not fetch content. Please paste the job description manually."})

    return JSONResponse(content=result)


@app.post("/analyze/v2/text")
async def analyze_v2_text(request: Request):
    payload = await request.json()
    job_text = payload.get("job_text")
    if not job_text or not isinstance(job_text, str) or len(job_text.strip()) < 150:
        raise HTTPException(status_code=400, detail={"error": "Please paste a job description of at least 150 characters."})

    try:
        result = run_agent_v2_from_text(job_text.strip())
        print(f"[BACKEND] Returning: {json.dumps(result, indent=2)}", flush=True)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})

    return JSONResponse(content=result)


@app.get("/profile")
def profile():
    entries = []
    data_dir = "data"
    if os.path.isdir(data_dir):
        for filename in sorted(os.listdir(data_dir)):
            if filename.endswith(".md") and filename != "cv.md":
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        entries.append({"filename": filename, "content": file.read()})
                except OSError:
                    continue
    return JSONResponse(content={"files": entries})
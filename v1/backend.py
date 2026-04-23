#backend.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from agent import run_agent

app = FastAPI()

@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse("index.html")

@app.post("/analyze")
async def analyze(request: Request):
    payload = await request.json()
    url = payload.get("url")
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=400, detail={"error": "A valid 'url' field is required."})

    try:
        result = run_agent(url.strip())
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

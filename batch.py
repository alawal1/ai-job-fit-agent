import json
import os
from datetime import date
from agent import run_agent
import openpyxl

os.makedirs("outputs", exist_ok=True)

def save_to_tracker(result, url, filepath="tracker.xlsx"):
    try:
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Company", "Position", "Industry", "Fit Score", "Decision", "URL", "Date"])
    
    ws.append([
        result.get("company", ""),
        result.get("position", ""),
        result.get("industry", ""),
        result.get("fit_score", ""),
        result.get("decision", ""),
        url,
        str(date.today())
    ])
    wb.save(filepath)

with open("data/jobs/urls.txt", "r") as url_file:
    urls = [line.strip() for line in url_file if line.strip()]

for i, url in enumerate(urls):
    print(f"\nAnalyzing job {i+1}/{len(urls)}: {url}")
    try:
        result = run_agent(url)
        
        with open(f"outputs/job_{i+1}.md", "w") as f:
            f.write(f"# {result.get('company')} — {result.get('position')}\n\n")
            f.write(f"**Fit Score:** {result.get('fit_score')}/100\n")
            f.write(f"**Decision:** {result.get('decision', '').upper()}\n\n")
            f.write(f"## Reasoning\n{result.get('reasoning', '')}\n\n")
            f.write(f"## Matches\n")
            for m in result.get("matches", []):
                f.write(f"- {m}\n")
            f.write(f"\n## Gaps\n")
            for g in result.get("gaps", []):
                f.write(f"- {g}\n")

        if result.get("decision") == "apply":
            save_to_tracker(result, url)
            print(f"✓ {result.get('company')} — {result.get('fit_score')}/100 — APPLY → saved to tracker")
        else:
            print(f"✗ {result.get('company')} — {result.get('fit_score')}/100 — SKIP")

    except Exception as e:
        import traceback
        traceback.print_exc()
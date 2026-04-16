import json
import os
from datetime import date
from agent import run_agent
import openpyxl

os.makedirs("outputs", exist_ok=True)
for file in os.listdir("outputs"):
    if file.endswith(".md"):
        os.remove(os.path.join("outputs", file))
        
def save_to_tracker(result, url, filepath="tracker.xlsx"):
    try:
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Company", "Position", "Industry", "Fit Score", "Decision", "Matches", "Gaps", "Reasoning", "URL", "Date"])
    
        ws.append([
            result.get("company", ""),
            result.get("position", ""),
            result.get("industry", ""),
            result.get("fit_score", ""),
            result.get("decision", ""),
            ", ".join(result.get("matches", [])),
            ", ".join(result.get("gaps", [])),
            result.get("reasoning", ""),
            url,
            str(date.today())
    ])  
    wb.save(filepath)

def already_tracked(url, filepath="tracker.xlsx"):
    try:
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
        for row in ws.iter_rows(values_only=True):
            if url in row:
                return True
    except FileNotFoundError:
        pass
    return False

with open("data/jobs/urls.txt", "r") as url_file:
    urls = [line.strip() for line in url_file if line.strip()]

for i, url in enumerate(urls):
    print(f"\nAnalyzing job {i+1}/{len(urls)}: {url}")
    if already_tracked(url):
        print(f"↷ Already in tracker, skipping")
        continue
    try:
        result = run_agent(url)
        
        
        company_name = result.get('company', f'job_{i+1}').replace(" ", "_").lower()
        with open(f"outputs/{company_name}.md", "w") as f:
            f.write(f"# {result.get('company')} — {result.get('position')}\n\n")
            f.write(f"**Fit Score:** {result.get('fit_score')}/100\n")
            final_decision = "apply" if result.get("fit_score", 0) >= 70 else "skip"
            f.write(f"**Decision:** {final_decision.upper()}\n\n")            
            f.write(f"## Reasoning\n{result.get('reasoning', '')}\n\n")
            f.write(f"## Matches\n")
            for m in result.get("matches", []):
                f.write(f"- {m}\n")
            f.write(f"\n## Gaps\n")
            for g in result.get("gaps", []):
                f.write(f"- {g}\n")

        if result.get("fit_score", 0) >= 70:
            save_to_tracker(result, url)
            print(f"✓ {result.get('company')} — {result.get('fit_score')}/100 — APPLY → saved to tracker")
        else:
            print(f"✗ {result.get('company')} — {result.get('fit_score')}/100 — SKIP")

    except Exception as e:
        import traceback
        traceback.print_exc()
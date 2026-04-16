import argparse
from agent import run_agent, load_cv, fetch_job_posting

# print("Script started")
parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, help="Path to job description file")
parser.add_argument("--job", type=str, help="Job description or URL")
args = parser.parse_args()
cv = load_cv("data/cv.md")
print("STEP: job description loaded")
    
def print_report(result):
    print("\n=== JOB FIT ANALYSIS ===\n")
    print(f"Decision: {result['decision'].upper()}")
    print(f"Fit Score: {result['fit_score']}\n")

    if result["decision"] == "skip":
        print(f"Reason: {result.get('skip_reason', '')}")
        return

    print(f"Reason: {result.get('fit_reason', '')}\n")

    print("Top Matches:")
    for m in result["analysis"].get("match", []):
        print(f"- {m}")

    gaps = result["analysis"].get("gaps", [])

    print("\nGaps:")
    if gaps:
        for g in gaps:
            print(f"- {g}")
    else:
        print("No major gaps identified.")

    print("\n=== IMPROVED CV ===")
    print(result["improved_cv"])
    

def save_markdown_report(result, filename="report.md"):
    with open(filename, "w") as f:
        f.write("# Job Fit Analysis\n\n")
        f.write(f"**Decision:** {result['decision'].upper()}\n")
        f.write(f"**Fit Score:** {result['fit_score']}\n\n")

        if result["decision"] == "skip":
            f.write(f"**Reason:** {result.get('skip_reason', '')}\n")
            return

        f.write("## Reason\n")
        f.write(result.get("fit_reason", "") + "\n\n")

        f.write("## Matches\n")
        for m in result["analysis"].get("match", []):
            f.write(f"- {m}\n")

        f.write("\n## Gaps\n")
        gaps = result["analysis"].get("gaps", [])
        if gaps:
            for g in gaps:
                f.write(f"- {g}\n")
        else:
            f.write("No major gaps identified.\n")

        f.write("\n## Improved CV\n")
        f.write(result["improved_cv"])


print("STEP: starting input handling")

if args.file:
    with open(args.file, "r") as f:
        print(f"STEP: reading file {args.file}")
        job_description = f.read()

elif args.job:
    print(f"STEP: received job input: {args.job[:50]}...")
    if args.job.startswith("http"):
        from agent import fetch_job_posting
        job_description = fetch_job_posting(args.job)
        print("STEP: fetched job from URL")
    else:
        job_description = args.job

else:
    print("Please provide --job or --file")
    exit()

print("STEP: running agent...")
try:
    result = run_agent(job_description, cv)
    print("STEP: agent finished")
except Exception as e:
    print("ERROR:", e)

print("STEP: about to print report")
print_report(result)
save_markdown_report(result, "output.md")
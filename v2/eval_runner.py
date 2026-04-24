# eval_runner.py
"""
Runs the triage agent against an eval set and reports agreement with manual verdicts.
"""
import csv
import json
from collections import Counter
from agent import run_agent_v2, client

EVAL_FILE = "data/eval_set.csv"


def extract_verdict_from_result(result: dict) -> str:
    """
    The agent returns its verdict inside final_message as text.
    We look for the verdict word. Crude but works for now.
    """
    msg = (result.get("final_message") or "").lower()
    # Order matters: check 'borderline' before 'apply' and 'skip'
    if "borderline" in msg:
        return "borderline"
    if "skip" in msg:
        return "skip"
    if "apply" in msg:
        return "apply"
    return "unknown"


def main():
    rows = []
    with open(EVAL_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "url": row["url"].strip(),
                "my_verdict": row["my_verdict"].strip().lower(),
                "my_notes": row["my_notes"].strip(),
            })

    results = []
    for i, row in enumerate(rows):
        print(f"\n--- [{i+1}/{len(rows)}] {row['url'][:80]}")
        try:
            agent_result = run_agent_v2(row["url"])
            agent_verdict = extract_verdict_from_result(agent_result)
            agreement = "✓" if agent_verdict == row["my_verdict"] else "✗"
        except Exception as e:
            agent_verdict = "error"
            agreement = "!"
            agent_result = {"error": str(e)}

        print(f"  mine:  {row['my_verdict']}")
        print(f"  agent: {agent_verdict}  {agreement}")

        results.append({
            "url": row["url"],
            "my_verdict": row["my_verdict"],
            "my_notes": row["my_notes"],
            "agent_verdict": agent_verdict,
            "tool_calls_made": agent_result.get("tool_calls_made"),
            "iterations": agent_result.get("iterations"),
            "final_message": agent_result.get("final_message", ""),
        })

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    agreements = sum(1 for r in results if r["agent_verdict"] == r["my_verdict"])
    print(f"Agreement: {agreements}/{len(results)} ({100*agreements/len(results):.0f}%)")

    # Confusion breakdown
    print("\nConfusion:")
    confusion = Counter()
    for r in results:
        confusion[(r["my_verdict"], r["agent_verdict"])] += 1
    for (mine, agent), count in sorted(confusion.items()):
        marker = "  " if mine == agent else "→ "
        print(f"  {marker}mine={mine:10} agent={agent:10} n={count}")

    # Save detailed results
    with open("data/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed results → data/eval_results.json")

    client.close()


if __name__ == "__main__":
    main()
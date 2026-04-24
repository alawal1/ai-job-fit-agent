# agent_v2.py
"""
Job Triage Agent (v2).

Replaces v1's fit-score pipeline with a triage agent that decides
apply / borderline / skip. Uses OpenAI's tool-calling loop.

Current state: minimum viable. Only fetch + extract tools are wired up.
The remaining three tools (check_hard_filters, assess_fit, search_company_context)
will be added one at a time.
"""
import json
from openai import OpenAI
from dotenv import load_dotenv

from skills.fetch_job import fetch_job_posting
from skills.extract_signals import extract_job_signals
from skills.check_filters import check_hard_filters
from skills.assess_fit import assess_fit

load_dotenv()
client = OpenAI()
with open("data/profile.json") as f:
    PROFILE = json.load(f)

MAX_ITERATIONS = 8
MODEL = "gpt-4o"


# Tool schemas shown to the LLM.
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_job_posting",
            "description": (
                "Fetches the text content of a job posting from a URL. "
                "Call this first whenever you are given a URL. Returns plain text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL of the job posting"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_job_signals",
            "description": (
                "Extracts the specific fields needed to triage a job posting from its full text. "
                "Call this after fetch_job_posting has returned the posting text. "
                "Do not call if the text is under ~150 words, appears truncated, or is mostly "
                "boilerplate (company description, benefits list) without actual role content. "
                "Returns a structured signals object. This tool focuses only on triage-relevant "
                "fields; it does NOT extract the full requirements list."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_text": {
                        "type": "string",
                        "description": "The full text of the job posting, as returned by fetch_job_posting.",
                    },
                },
                "required": ["job_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_hard_filters",
            "description": (
                "Checks whether a job passes the candidate's hard filters (language and seniority). "
                "Call this after extract_job_signals has returned successfully. "
                "You MUST pass the full signals object returned by extract_job_signals as the 'signals' argument. "
                "Do not call this tool without the signals argument. "
                "If this returns passed=false, the triage is complete — return a skip verdict immediately. "
                "Do not call assess_fit when hard filters fail."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "signals": {
                        "type": "object",
                        "description": "The signals object returned by extract_job_signals.",
                    },
                },
                "required": ["signals"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assess_fit",
            "description": (
                "Evaluates how well a job matches the candidate's profile. "
                "Call only after check_hard_filters has returned passed=true. "
                "You MUST pass the full signals object as the 'signals' argument. "
                "Returns a verdict (apply/borderline/skip) with confidence and structured reasoning. "
                "If verdict is 'borderline' with non-empty open_questions, you may call this tool "
                "a second time later with a 'company_context' argument (not yet supported — only call once for now)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "signals": {
                        "type": "object",
                        "description": "The signals object returned by extract_job_signals.",
                    },
                },
                "required": ["signals"],
            },
        },
    },
]


# Runtime implementations. Tools that need the OpenAI client get it passed in.
def _execute_tool(name: str, args: dict) -> dict:
    print(f"[TOOL CALLED] name={name} args_keys={list(args.keys())}", flush=True)

    if name == "fetch_job_posting":
        text = fetch_job_posting(args["url"])
        result = {"text": text, "length_chars": len(text)}
    elif name == "extract_job_signals":
        result = extract_job_signals(args["job_text"], client)
    elif name == "check_hard_filters":
        if "signals" not in args:
            result = {"error": "Missing 'signals' argument. You must pass the signals object from extract_job_signals."}
        else:
            result = check_hard_filters(args["signals"], PROFILE, client)
    elif name == "assess_fit":
        if "signals" not in args:
            result = {"error": "Missing 'signals' argument. You must pass the signals object from extract_job_signals."}
        else:
            result = assess_fit(args["signals"], PROFILE, client)
    else:
        result = {"error": f"Unknown tool: {name}"}

    print(f"[TOOL RESULT] {name} → {json.dumps(result, ensure_ascii=False)[:300]}", flush=True)
    return result

SYSTEM_PROMPT = """You are a job triage agent. You decide whether a job posting is worth the user applying to: apply, borderline, or skip.

Required workflow:
1. Call fetch_job_posting to get the text.
2. Call extract_job_signals on the text — unless it's a dead link or boilerplate page.
3. Call check_hard_filters on the signals.
4. If check_hard_filters returns passed=false, return verdict SKIP with the failure reasons. Do not call more tools.
5. If check_hard_filters returns passed=true, return a brief summary with verdict APPLY (full fit assessment coming in a future tool).
6. Return the assess_fit verdict (apply/borderline/skip), confidence, and reasoning as your final answer.

Do not produce a final answer on a live posting without calling extract_job_signals and check_hard_filters.
Efficiency matters: do not call any tool more than once unnecessarily."""

def run_agent_v2(url: str) -> dict:
    """
    Run the v2 triage agent on a single job URL.

    Args:
        url: The job posting URL to analyze.

    Returns:
        dict with the agent's final output, plus metadata:
            - final_message: the agent's textual response
            - tool_calls_made: count of tool calls in this run
            - iterations: number of loop iterations
            - error: present if the loop terminated abnormally
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this job posting: {url}"},
    ]

    tool_calls_made = 0

    for iteration in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            temperature=0,
        )
        choice = response.choices[0]
        message = choice.message
        messages.append(message)

        if choice.finish_reason == "stop":
            return {
                "final_message": message.content,
                "tool_calls_made": tool_calls_made,
                "iterations": iteration + 1,
            }

        if choice.finish_reason == "tool_calls":
            for tool_call in message.tool_calls:
                tool_calls_made += 1
                print(f"[LOOP] iter={iteration} call#{tool_calls_made} → {tool_call.function.name}", flush=True)
                args = json.loads(tool_call.function.arguments)
                try:
                    result = _execute_tool(tool_call.function.name, args)
                except Exception as e:
                    print(f"[TOOL ERROR] {tool_call.function.name}: {type(e).__name__}: {e}", flush=True)
                    result = {"error": f"{type(e).__name__}: {e}"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
            continue

        # Any other finish_reason (length, content_filter) — bail.
        return {
            "final_message": message.content or "",
            "tool_calls_made": tool_calls_made,
            "iterations": iteration + 1,
            "error": f"Unexpected finish_reason: {choice.finish_reason}",
        }

    # Hit iteration cap without natural termination.
    return {
        "final_message": "",
        "tool_calls_made": tool_calls_made,
        "iterations": MAX_ITERATIONS,
        "error": "Max iterations reached without natural termination.",
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agent_v2.py <job_url>")
        sys.exit(1)

    try:
        result = run_agent_v2(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    finally:
        print("DEBUG: about to close client", flush=True)
        client.close()
        print("DEBUG: client closed", flush=True)
# skills/check_filters.py
"""
Hard filter check: languages (deterministic) + seniority (LLM).

Rules:
1. Only languages explicitly named in the job are checked.
2. Only 'required' languages gate; 'preferred' are ignored.
3. Level 'unspecified' in the job is treated as 'fluent' for comparison.
4. Profile level must be >= job level.
5. All required languages must pass independently.
6. Seniority is judged by an LLM against the profile's natural-language description.
"""
import json

LEVEL_RANK = {"basic": 1, "conversational": 2, "fluent": 3, "native": 4}
UNSPECIFIED_DEFAULT = "fluent"


def _check_languages(job_languages, profile_languages):
    failures = []
    for lang in job_languages:
        if lang.get("required_or_preferred") != "required":
            continue

        required_level = lang["level"] if lang["level"] != "unspecified" else UNSPECIFIED_DEFAULT
        profile_entry = next(
            (p for p in profile_languages if p["language"].lower() == lang["language"].lower()),
            None,
        )

        if profile_entry is None:
            failures.append(f"Job requires {lang['language']} ({required_level}); not in profile.")
            continue

        if LEVEL_RANK[profile_entry["level"]] < LEVEL_RANK[required_level]:
            failures.append(
                f"Job requires {lang['language']} at {required_level}; profile has {profile_entry['level']}."
            )

    if failures:
        return {"filter": "language", "passed": False, "reason": " ".join(failures)}
    return {"filter": "language", "passed": True, "reason": "All required languages satisfied."}


SENIORITY_PROMPT = """You are checking whether a job's seniority level matches a candidate's acceptability criteria.

Job title: {title}
Job seniority signals:
- title_level: {title_level}
- years_experience_required: {years}
- role_context_snippet: {snippet}

Candidate's acceptability criteria:
{seniority_description}

Is this role acceptable for the candidate based on seniority? Respond with a JSON object:
{{"passed": true/false, "reason": "one sentence explanation"}}

Return ONLY the JSON object. No preamble."""


def _check_seniority(signals, profile_seniority_description, client):
    indicators = signals.get("seniority_indicators", {})
    prompt = SENIORITY_PROMPT.format(
        title=signals.get("job_title", "unknown"),
        title_level=indicators.get("title_level", "unspecified"),
        years=indicators.get("years_experience_required", "unspecified"),
        snippet=indicators.get("role_context_snippet", ""),
        seniority_description=profile_seniority_description,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return {
            "filter": "seniority",
            "passed": bool(result["passed"]),
            "reason": result.get("reason", ""),
        }
    except (json.JSONDecodeError, KeyError) as e:
        return {
            "filter": "seniority",
            "passed": False,
            "reason": f"Seniority check failed to parse: {e}",
        }


def check_hard_filters(signals: dict, profile: dict, client) -> dict:
    """
    Run hard filters. Returns pass/fail + per-filter reasoning.

    Short-circuits: if language fails, skip the seniority LLM call.
    """
    results = []
    llm_calls = 0

    lang_result = _check_languages(
        signals.get("required_languages", []),
        profile["hard_filters"]["languages"],
    )
    results.append(lang_result)

    if not lang_result["passed"]:
        return {"passed": False, "filter_results": results, "llm_calls_made": 0}

    seniority_result = _check_seniority(
        signals,
        profile["hard_filters"]["seniority_description"],
        client,
    )
    results.append(seniority_result)
    llm_calls += 1

    passed = all(r["passed"] for r in results)
    return {"passed": passed, "filter_results": results, "llm_calls_made": llm_calls}
# skills/assess_fit.py
"""
Soft-judgment tool: apply / borderline / skip + confidence + structured reasoning.

Called only after check_hard_filters returns passed=true.
Can be called twice per analysis: once without company_context, once with (if borderline).
"""
import json

ASSESS_PROMPT = """You are evaluating whether a job posting is a good fit for a candidate.

Return a verdict: apply, borderline, or skip.

- apply: clear fit. Role aligns with work description and candidate has relevant strengths.
- skip: clear non-fit. Role is off- work description, wrong domain, or gaps are substantial.
- borderline: genuinely unclear. Use this ONLY when you can articulate specific open_questions that would change the verdict if answered.

Do not use 'borderline' as a hedge. If you cannot name concrete open_questions, pick apply or skip.

CANDIDATE PROFILE:
"""

ASSESS_PROMPT_TAIL = """

RETURN JSON with this exact shape:
{
  "verdict": "apply" | "borderline" | "skip",
  "confidence": "high" | "medium" | "low",
  "reasoning": {
    "strengths": ["2-5 concrete matches between posting and profile"],
    "gaps": ["0-5 requirements in the posting not covered by profile"],
    "open_questions": ["Empty if verdict is high-confidence apply/skip. Non-empty for borderline."]
  }
}

Return ONLY the JSON object. No preamble."""


def assess_fit(signals: dict, profile: dict, client, company_context: dict | None = None) -> dict:
    """
    Evaluate fit. Returns verdict + confidence + reasoning + enrichment_used flag.
    """
    prompt = (
        ASSESS_PROMPT
        + json.dumps(profile, indent=2)
        + "\n\nJOB SIGNALS:\n"
        + json.dumps(signals, indent=2)
    )

    if company_context is not None:
        prompt += "\n\nCOMPANY CONTEXT (from prior search):\n" + json.dumps(company_context, indent=2)

    prompt += ASSESS_PROMPT_TAIL

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    try:
        result = json.loads(response.choices[0].message.content)
        result["enrichment_used"] = company_context is not None
        return result
    except json.JSONDecodeError as e:
        return {
            "verdict": "skip",
            "confidence": "low",
            "reasoning": {"strengths": [], "gaps": [], "open_questions": []},
            "enrichment_used": company_context is not None,
            "error": f"Failed to parse LLM response: {e}",
        }
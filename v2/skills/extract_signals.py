# skills/extract_signals.py
"""
Extracts triage-relevant signals from a job posting.

This is an LLM-backed tool — it makes one OpenAI call with a tight prompt
to pull out only the fields needed for triage decisions (not the full
requirements list).
"""
import json


EXTRACTION_PROMPT = """You are extracting triage-relevant signals from a job posting.

Extract ONLY the following fields. Do not extract the full requirements list.

Return a JSON object with these exact keys:
- job_title: string
- company_name: string
- location: string (as written in the posting, e.g. "Stockholm, Sweden (Hybrid)")
- required_languages: array of objects with keys {language, level, required_or_preferred}
    - level must be one of: "basic", "conversational", "fluent", "native", "unspecified"
    - required_or_preferred must be one of: "required", "preferred"
    - Only include languages EXPLICITLY mentioned. Do not assume English.
    - If level is not stated, use "unspecified".
    - "must have", "required" → required; "nice to have", "preferred", "plus" → preferred
- seniority_indicators: object with keys {title_level, years_experience_required, role_context_snippet}
    - title_level: the seniority word in the title (e.g. "Junior", "Senior", "Associate"), or "unspecified"
    - years_experience_required: as written (e.g. "3+ years", "unspecified")
    - role_context_snippet: 1-2 sentences from the posting describing role seniority context
- key_skills_mentioned: array of strings, up to 10 technical or domain skills named
- extraction_confidence: "high" | "medium" | "low"
    - Set to "low" if the posting was vague, fragmentary, or missing key triage info.

Return ONLY the JSON object. No preamble, no code fences, no commentary.

Job posting text:
---
{job_text}
---
"""


def extract_job_signals(job_text: str, client) -> dict:
    """
    Extract triage-relevant signals from job posting text.

    Args:
        job_text: Full text of the job posting, as returned by fetch_job_posting.
        client: OpenAI client instance.

    Returns:
        dict with keys: job_title, company_name, location, required_languages,
        seniority_indicators, key_skills_mentioned, extraction_confidence.

    Raises:
        ValueError: If the LLM response cannot be parsed as JSON.
    """
    if not job_text or len(job_text.strip()) < 150:
        # Don't spend an LLM call on text that's clearly insufficient.
        return {
            "job_title": "",
            "company_name": "",
            "location": "",
            "required_languages": [],
            "seniority_indicators": {
                "title_level": "unspecified",
                "years_experience_required": "unspecified",
                "role_context_snippet": "",
            },
            "key_skills_mentioned": [],
            "extraction_confidence": "low",
        }

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(job_text=job_text)}],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"extract_job_signals: could not parse LLM response as JSON: {e}\nResponse: {content}")
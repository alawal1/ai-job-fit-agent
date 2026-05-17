"""
CV improvement suggestions tool.

Given job signals, assess_fit reasoning, and user's CV, returns strategic
recommendations (what to emphasize, reorder, add) without rewriting bullets.
"""
import json


def suggest_cv_improvements(signals: dict, assess_fit_reasoning: dict, cv_path: str = "data/cv.md") -> dict:
    """
    Generate CV improvement suggestions for a specific job.
    
    Args:
        signals: Job signals from extract_job_signals
        assess_fit_reasoning: The reasoning dict from assess_fit (strengths, gaps, open_questions)
        cv_path: Path to CV markdown file
        
    Returns:
        {
            "recommendations": [...],  # Strategic suggestions
            "cv_gaps": [...]            # What's missing from CV vs job
        }
    """
    # Load CV
    try:
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_text = f.read()
    except FileNotFoundError:
        return {"error": f"CV file not found at {cv_path}"}
    
    # Build prompt
    prompt = f"""You are a CV coach. Given a job posting's requirements and the candidate's CV, suggest strategic improvements.

Job signals:
{json.dumps(signals, indent=2)}

Fit assessment (already done):
Strengths: {assess_fit_reasoning.get('strengths', [])}
Gaps: {assess_fit_reasoning.get('gaps', [])}

Candidate's CV:
---
{cv_text}
---

Provide:
1. **recommendations**: 3-5 specific, actionable suggestions (e.g., "Lead with your Azure DevOps experience in skills section", "Add a bullet about stakeholder coordination in the KPMG role"). Do NOT rewrite bullets — only suggest what to emphasize, reorder, or add.
2. **cv_gaps**: What the job requires that's genuinely missing from the CV (not just under-emphasized).

Return ONLY valid JSON with no preamble:
{{
  "recommendations": ["...", "..."],
  "cv_gaps": ["...", "..."]
}}
"""
    
    # Use same OpenAI client pattern as other tools
    from openai import OpenAI
    client = OpenAI()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        result = json.loads(response.choices[0].message.content)
        return result
    finally:
        client.close()
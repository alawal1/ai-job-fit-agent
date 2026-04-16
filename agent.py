from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv() # Loads API key from .env file
client = OpenAI() # Creates client (connection to the AI)

def load_cv(filepath):
    with open(filepath, "r") as file:
        return file.read(
        )

# DATA LOADING        
cv = load_cv("data/cv.md")
experience = load_cv("data/experience.md")
education = load_cv("data/education.md")
skills = load_cv("data/skills.md")
projects = load_cv("data/projects.md")
positioning = load_cv("data/positioning.md")

def safe_json_load(content):
        try:
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw": content}

def check_language(job_description):  # Detect if job requires Swedish (filter step)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You detect if a job requires Swedish."
            },
            {
                "role": "user",
                "content": f"""
                Does this job require Swedish?

                Return ONLY JSON:
                {{
                "requires_swedish": true/false,
                "reason": "short explanation (e.g. 'explicit Swedish requirement' or 'only optional')"
                }}

                Be precise. Always fill the reason field.

                Job description:
                {job_description}
                """
                    }
                ]
            )

    content = response.choices[0].message.content
    return safe_json_load(content)
    
def extract_job_requirements(job_description): # Extract structured requirements from job description
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You extract key skills and requirements from job descriptions and return them in a structured JSON format."
            },
            {
                "role": "user",
                "content": f"""
                    Extract the key requirements from this job description.

                    Return ONLY valid JSON in this format:
                    {{
                    "skills": [],
                    "tools": [],
                    "experience": []
                    }}

                    Job description:
                    {job_description}
                    """
                        }
                    ]
                )

    content = response.choices[0].message.content
    return safe_json_load(content)

def select_relevant_experience(profile, job_requirements): # Select most relevant parts of profile for the job
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You select the most relevant experience for a job."
            },
            {
                "role": "user",
                "content": f"""
                From the profile below, select ONLY the most relevant experiences for the job.

                Return ONLY JSON:
                {{
                "relevant_experience": []
                }}

                Profile:
                {profile}

                Job requirements:
                {job_requirements}
                """
            }
        ]
    )

    content = response.choices[0].message.content
    return safe_json_load(content)

def analyze_cv(cv, job_requirements): #  Evaluate match between profile and job
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You analyze CVs against job requirements."
            },
            {
                "role": "user",
                "content": f"""
                You are a career advisor.

                Compare the CV to the job requirements.

                Be precise and infer skills if they are implicitly shown.

                Return ONLY valid JSON in this format:
                {{
                "match": [],
                "gaps": []
                }}

                CV:
                {cv}

                Job requirements:
                {job_requirements}
                """
                            }
                        ]
                    )

    content = response.choices[0].message.content
    return safe_json_load(content)

def rewrite_cv(cv, job_requirements, analysis): #  Evaluate match between profile and job
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert career consultant who improves CVs."
            },
            {
                "role": "user",
                "content": f"""
                You are an expert career consultant.

                Improve the CV to better match the job requirements and identified gaps.

                Focus on:
                - highlighting relevant experience
                - rephrasing existing experience to better match the role
                - addressing gaps where possible (without lying)

                Return the improved CV in clear bullet points.

                Rules:
                - Only output the improved CV
                - Do NOT include explanations, notes, or comments


                Full profile:
                {cv}

                Job requirements:
                {job_requirements}

                Relevant experience:
                {analysis}
                """
                            }
                        ]
                    )

    return response.choices[0].message.content

def score_fit(profile, job_requirements): # Score how well the profile matches the job (0–100%)    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You evaluate how well a candidate fits a job."
            },
            {
                "role": "user",
                "content": f"""
                Evaluate the fit between the profile and job requirements.

                Return ONLY JSON:
                {{
                "fit_score": 0-100,
                "reason": ""
                }}

                Profile:
                {profile}

                Job requirements:
                {job_requirements}
                """
            }
        ]
    )

    content = response.choices[0].message.content
    return safe_json_load(content)

# SAVE 
def save_result(result, job_id):
    with open(f"outputs/result_{job_id}.json", "w") as file:
        json.dump(result, file, indent=4)
# AGENT
def run_agent(job_description, cv):

    # 1. Check language
    language_check = check_language(job_description)
    if language_check["requires_swedish"]:
        return {
            "decision": "skip",
            # "skip_reason": "Swedish required",
            "fit_score": 0,
            "skip_reason": language_check.get("reason", "Language requirement")
        }

    # 2. Extract requirements from job
    requirements = extract_job_requirements(job_description)

    # 3. Build full profile 
    full_profile = f"{cv}\n\n{experience}\n\n{education}\n\n{skills}\n\n{projects}\n\n{positioning}"

    # 4. Select relevant experience
    selected = select_relevant_experience(full_profile, requirements)

    # 5. Analyze fit 
    analysis = analyze_cv(full_profile, requirements)
    fit = score_fit(full_profile, requirements)
    decision = "apply" if fit["fit_score"] >= 60 else "skip"
    
    # 6. Rewrite CV using selected experience
    new_cv = rewrite_cv(full_profile, requirements, selected)

    # 7. Return result
   
    return {
        "decision": decision,
        "fit_score": fit["fit_score"],
        "fit_reason": fit["reason"],
        "requirements": requirements,
        "selected_experience": selected,
        "analysis": analysis,
        "improved_cv": new_cv
    }
    

# TESTS 

jobs = [
    """Consultant role requiring Python, data analysis, stakeholder management. ESG is a plus.""",

    """Product analyst role requiring SQL, dashboards, and business insights. No Swedish required.""",

    """Consulting role requiring Swedish and client interaction."""
]

# for i, job in enumerate(jobs):
#     print(f"\n--- JOB {i+1} ---")

#     result = run_agent(job, cv)
    
#     save_result(result, i+1)
    
#     if result["decision"] == "skip":
#         print("SKIP:", result.get("skip_reason", ""))
#     else:
#         print("FIT SCORE:", result.get("fit_score", "N/A")) 
#         print("REASON:", result.get("fit_reason", ""))
#         print(result["analysis"])
#         # print(result["improved_cv"])

# print(result["skills"])

# run skills
# requirements = extract_job_requirements(job_description)
# analysis = analyze_cv(cv, requirements)
# print(analysis)

# new_cv = rewrite_cv(cv, requirements, analysis)
# print(new_cv)
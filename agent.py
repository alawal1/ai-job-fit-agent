from openai import OpenAI
from dotenv import load_dotenv #  reads .env file 
import json
import os
from requests.exceptions import RequestException


load_dotenv()
client = OpenAI()

def fetch_job_posting(url: str) -> str:
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except RequestException as exc:
        raise RuntimeError(f"Failed to fetch job posting: {exc}") from exc

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)[:6000]

# def fetch_job_posting(url: str) -> str:
#     import requests
#     from bs4 import BeautifulSoup
#     r = requests.get(url, timeout=10)
#     soup = BeautifulSoup(r.text, "html.parser")
#     for tag in soup(["script", "style", "nav", "footer"]):
#         tag.decompose()
#     return soup.get_text(separator="\n", strip=True)[:6000]

def load_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


def load_full_profile() -> str:
    combined = ""
    for filename in os.listdir("data"):
        if filename.endswith(".md") and filename != "cv.md":
            filepath = os.path.join("data", filename)
            combined += load_file(filepath) + "\n\n"
    return combined

def parse_result(text: str) -> dict:
    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"error": "Could not parse result", "raw": text}


# TOOLS

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_job_posting",
            "description": "Fetches the text content of a job posting from a URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL of the job posting"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_full_profile",
            "description": "Loads the candidate's full profile including CV, experience, education, skills, projects and positioning.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
# TOOL DICTIONARY / TRAJECTORY
TOOLS = {
    "fetch_job_posting": fetch_job_posting,
    "load_full_profile": load_full_profile,
}

def run_agent(url: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """You are a job fit analyzer. Given a job posting URL:
            Rules:
            - If given a URL, always call fetch_job_posting first
            - Always call load_full_profile to get candidate data
            - Never guess or invent information
            - Only reason after you have tool outputs
            - matches and gaps in excel tracker file must be short keywords or skill names only (2-3 words max), never full sentences
            - cv_recommendations.add: specific skills or experiences worth adding to the CV for this role
            - cv_recommendations.remove: sections or skills that may confuse or weaken this specific application 

            Return ONLY valid JSON, no other text:
            {
                "company": "",
                "position": "",
                "industry": "",
                "fit_score": 0,
                "decision": "apply/skip",
                "matches": [],
                "gaps": [],
                "reasoning": "",
                "cv_recommendations": {
                    "add": [],
                    "remove": []
                }               
            } 
            Rules for the output:
            - fit_score is 0-100, never 0-10
            - - Ignore geography as a gap unless the job explicitly requires a specific country or city other than Stockholm
            - Use "you" and "your" when referring to the candidate, never their name
            - Penalize missing required skills, not just nice-to-haves
            - Do not round up or be generous. Err on the side of lower scores.
            """
            
        },
        {
            "role": "user",
            "content": f"Analyze this job posting for fit: {url}"
        }
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            tools=TOOL_DEFINITIONS,
            messages=messages,
            temperature=0
        )
        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason == "stop":
            return parse_result(message.content)

        if response.choices[0].finish_reason == "tool_calls":
            for tool_call in message.tool_calls:
                fn = TOOLS[tool_call.function.name]
                args = json.loads(tool_call.function.arguments)
                result = fn(**args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
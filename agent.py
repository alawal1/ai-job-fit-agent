from openai import OpenAI
from dotenv import load_dotenv #  reads .env file 
import json

load_dotenv()
client = OpenAI()


def fetch_job_posting(url: str) -> str:
    import requests
    from bs4 import BeautifulSoup
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)[:6000]

def load_cv(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()

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
            "name": "load_cv",
            "description": "Loads the candidate CV from a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the CV file"}
                },
                "required": ["filepath"]
            }
        }
    }
]

TOOLS = {
    "fetch_job_posting": fetch_job_posting,
    "load_cv": load_cv,
}

def run_agent(url: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """You are a job fit analyzer. Given a job posting URL:
            1. Fetch the job posting
            2. Load the candidate CV from data/cv.md
            3. Analyze the fit between the CV and the job
            4. Check if Swedish is required - if yes, recommend skipping
            5. Return a verdict with: fit_score (0-100), decision (apply/skip), and reasoning"""
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
            messages=messages
        )

        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason == "stop":
            return message.content

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
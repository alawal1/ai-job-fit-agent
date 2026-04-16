import sys
from agent import run_agent

if len(sys.argv) < 2:
    print("Usage: python main.py <job_url>")
    sys.exit(1)

url = sys.argv[1]
result = run_agent(url)
print(result)
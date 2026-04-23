# debug_fetch.py
from skills.fetch_job import fetch_job_posting

URL = "https://jobs.msd.com/gb/en/job/MSD1GBR393946ENGB/Business-Intelligence-Analyst?utm_source=linkedin&utm_medium=phenom-feeds"

text = fetch_job_posting(URL)
print(f"Length: {len(text)} chars")
print("---")
print(text[:2000])
print("---")
print("...")
print(text[-2000:])
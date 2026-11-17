import os
import re
import sys
from datetime import date

import requests
from dotenv import load_dotenv

from job_database import clear_jobs, load_jobs, save_jobs, saved_query
from resume_reader import clean_text, extract_text, find_resume

# JSearch API
URL = "https://jsearch.p.rapidapi.com/search-v2"
HOST = "jsearch.p.rapidapi.com"
MAX_PAGES = 5
DEFAULT_PAGES = 3
# saved jobs older than this get a warning
STALE_DAYS = 30

# role: skill keywords (ties go to the first role)
ROLES = {
    "software developer": ["java", "c++", "c#", "python", "algorithms", "object oriented"],
    "web developer": ["html", "css", "javascript", "react", "node", "php"],
    "data analyst": ["sql", "excel", "tableau", "power bi", "pandas", "statistics"],
    "data scientist": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit learn", "nlp"],
    "mobile developer": ["android", "ios", "swift", "kotlin", "flutter", "react native"],
    "cybersecurity analyst": ["cybersecurity", "security", "penetration testing", "wireshark", "firewall", "siem"],
    "devops engineer": ["docker", "kubernetes", "aws", "azure", "jenkins", "terraform"],
}

# US state codes
STATES = (
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV "
    "NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC"
).split()


def pick_role(text):
    """Role whose keywords appear most in the resume, or software developer."""
    text = f" {text} "
    scores = {role: sum(f" {k} " in text for k in words) for role, words in ROLES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "software developer"


def is_student(text):
    """True if the resume says student/expected or has a future graduation year."""
    years = [int(y) for y in re.findall(r"\b20\d\d\b", text)]
    return "student" in text or "expected" in text or any(y > date.today().year for y in years)


def find_state(raw):
    """State code from the first "City, ST" in the resume, or USA."""
    for state in re.findall(r"[A-Za-z]+,\s*([A-Z]{2})\b", raw):
        if state in STATES:
            return state
    return "USA"


def build_query(resume_path):
    """Build the job search query from the resume."""
    raw = extract_text(resume_path)
    text = clean_text(raw)
    level = "entry level " if is_student(text) else ""
    return f"{level}{pick_role(text)} jobs in {find_state(raw)}"


def fetch_jobs(query, pages=DEFAULT_PAGES):
    """Call JSearch once and return the raw job list. Each page = 1 request credit."""
    load_dotenv()
    key = os.getenv("RAPIDAPI_KEY")
    if not key:
        raise ValueError("RAPIDAPI_KEY is missing. Add it to your .env file.")

    # one request, up to MAX_PAGES pages
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": HOST}
    params = {"query": query, "num_pages": max(1, min(pages, MAX_PAGES)), "country": "us"}
    # only jobs posted in the last month: remove the # from the next line.
    # Warning: this may return fewer jobs. Other choices: "week", "3days", "today".
    # params["date_posted"] = "month"
    response = requests.get(URL, headers=headers, params=params, timeout=60)

    # show the API's own error message
    if not response.ok:
        raise ValueError(f"API error {response.status_code}: {response.text[:200]}")
    return response.json().get("data", {}).get("jobs", [])


def clean_jobs(raw_jobs, query):
    """Keep only the fields we need ("n/a" if missing); skip jobs with no id or description."""
    jobs = []
    for job in raw_jobs:
        if not job.get("job_id") or not job.get("job_description"):
            continue
        jobs.append({
            "id": job["job_id"],
            "title": job.get("job_title") or "n/a",
            "company": job.get("employer_name") or "n/a",
            "description": " ".join(job["job_description"].split()),
            "link": job.get("job_apply_link") or "n/a",
            # site it was posted on (e.g. LinkedIn, Indeed)
            "source": job.get("job_publisher") or "n/a",
            "location": job.get("job_location") or "n/a",
            "job_type": job.get("job_employment_type") or "n/a",
            # date only (YYYY-MM-DD)
            "posted": (job.get("job_posted_at_datetime_utc") or "n/a")[:10],
            # search that found it, and when
            "query": query,
            "collected": date.today().isoformat(),
        })
    return jobs


def stale_note(jobs):
    """Warning if the saved jobs were collected more than STALE_DAYS ago (None if recent or unknown)."""
    collected = jobs[0].get("collected") if jobs else None
    if collected:
        days = (date.today() - date.fromisoformat(collected)).days
        if days > STALE_DAYS:
            return f"Note: your saved jobs were collected {days} days ago and may be out of date."
    return None


def collect(resume_path, pages=DEFAULT_PAGES, refresh=False):
    """Get jobs for the resume. Skips the API if jobs for this search are already saved (unless refresh)."""
    query = build_query(resume_path)
    print(f"Search: {query}")

    # same search already saved? use those (no API call)
    if saved_query() == query and not refresh:
        saved = load_jobs()
        print(f"Already have {len(saved)} jobs for this search. No API call needed.")
        note = stale_note(saved)
        if note:
            print(note)
        print(f"To get new jobs instead, run: python main.py collect {pages} --refresh")
        return

    # new search: get jobs first, then replace the old ones
    jobs = clean_jobs(fetch_jobs(query, pages), query)
    clear_jobs()
    saved = save_jobs(jobs)
    print(f"Got {len(jobs)} jobs, saved {saved} to data/jobs.db ({len(jobs) - saved} duplicates skipped)")


# run: python src/job_collector.py [pages 1-5]
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python src/job_collector.py [pages 1-5]")
        sys.exit(1)
    try:
        pages = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PAGES
        collect(find_resume(), pages)
    except (FileNotFoundError, ValueError, requests.RequestException) as e:
        print(f"Error: {e}")
        sys.exit(1)

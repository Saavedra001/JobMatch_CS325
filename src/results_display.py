import csv
import sys
from pathlib import Path

from job_collector import build_query
from job_database import load_jobs, saved_query
from matcher import match_jobs
from resume_reader import find_resume, read_resume

# results.csv in the project folder
RESULTS_PATH = Path(__file__).resolve().parent.parent / "results.csv"


def show_results(jobs):
    """Print the numbered job matches and the JSearch credit. Details that are "n/a" are skipped."""
    # print special characters (like "—") correctly on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not jobs:
        print("No matching jobs found.")
        return

    print(f"\nYour top {len(jobs)} job matches:\n")
    for i, job in enumerate(jobs, 1):
        # company | location | job type | posted date (skip "n/a")
        posted = f"Posted {job['posted']}" if job["posted"] != "n/a" else "n/a"
        details = [d for d in (job["company"], job["location"], job["job_type"], posted) if d != "n/a"]

        print(f"{i}. {job['title']}")
        if details:
            print("   " + " | ".join(details))
        if job.get("skills"):
            print(f"   Matched skills: {', '.join(job['skills'])}")
        if job["link"] != "n/a":
            print(f"   {job['link']}")
        print()

    print("Jobs data provided by JSearch")


def save_results(jobs):
    """Save all ranked jobs to results.csv (overwritten each time)."""
    try:
        # utf-8-sig so Excel shows special characters correctly
        with open(RESULTS_PATH, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["rank", "title", "company", "location", "job type", "posted", "matched skills", "link"])
            for i, job in enumerate(jobs, 1):
                row = [job["title"], job["company"], job["location"], job["job_type"], job["posted"],
                       ", ".join(job.get("skills", [])), job["link"]]
                writer.writerow([i] + [safe_cell(value) for value in row])
    except PermissionError:
        print(f"Could not save {RESULTS_PATH.name}. Is it open in Excel? Close it and run match again.")
        return
    print(f"All {len(jobs)} ranked jobs saved to {RESULTS_PATH.name}")


def safe_cell(value):
    """Stop spreadsheet apps from running job text that starts like a formula (e.g. "=...")."""
    return "'" + value if value[:1] in ("=", "+", "-", "@") else value


# quick test: python src/results_display.py
if __name__ == "__main__":
    try:
        path = find_resume()
        # saved jobs must come from this resume's search
        if saved_query() != build_query(path):
            print("No saved jobs for this resume yet. Run the collector first.")
            sys.exit(1)
        show_results(match_jobs(read_resume(path), load_jobs()))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

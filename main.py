import argparse
import sys
from pathlib import Path

# let main.py use the modules in src/
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import requests

from job_collector import build_query, collect
from job_database import load_jobs, saved_query
from matcher import match_jobs
from results_display import save_results, show_results
from resume_reader import find_resume, read_resume


def run_match():
    """Rank all saved jobs for the resume, print the top 5, and save all of them to results.csv."""
    path = find_resume()
    # saved jobs must come from this resume's search
    if saved_query() != build_query(path):
        raise ValueError("No saved jobs for this resume yet. Run: python main.py collect")
    jobs = load_jobs()
    ranked = match_jobs(read_resume(path), jobs, top_n=len(jobs))
    show_results(ranked[:5])
    save_results(ranked)


def main():
    # commands: collect [pages] [--refresh], match
    parser = argparse.ArgumentParser(description="Find the jobs that best match your resume (put it in resumes/).")
    commands = parser.add_subparsers(dest="command", required=True)
    collect_cmd = commands.add_parser("collect", help="get jobs for your resume from JSearch (uses API credits)")
    collect_cmd.add_argument("pages", nargs="?", type=int, default=1, choices=range(1, 6), metavar="pages",
                             help="pages to get, 1-5 (each page = up to 10 jobs = 1 credit). Default: 1")
    collect_cmd.add_argument("--refresh", action="store_true",
                             help="replace the saved jobs for this resume with new ones (uses credits)")
    commands.add_parser("match", help="show your top 5 job matches and save all ranked jobs to results.csv (no API calls)")
    args = parser.parse_args()

    try:
        if args.command == "collect":
            collect(find_resume(), args.pages, args.refresh)
        else:
            run_match()
    except (FileNotFoundError, ValueError, requests.RequestException) as e:
        print(f"Error: {e}")
        sys.exit(1)
    # Ctrl+C (or closed input) while running
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()

import argparse
import sys
from pathlib import Path

# let main.py use the modules in src/
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import requests

from job_collector import DEFAULT_PAGES, MAX_PAGES, build_query, collect, stale_note
from job_database import load_jobs, saved_query
from matcher import match_jobs
from results_display import save_results, show_results
from resume_reader import find_resume, read_resume


def run_match(show_all=False):
    """Rank all saved jobs for the resume, print the top 5 (or all), and save all of them to data/results.csv."""
    path = find_resume()
    # saved jobs must come from this resume's search
    if saved_query() != build_query(path):
        raise ValueError("No saved jobs for this resume yet. Run: python main.py collect")
    jobs = load_jobs()
    ranked = match_jobs(read_resume(path), jobs, top_n=len(jobs))
    show_results(ranked if show_all else ranked[:5])
    save_results(ranked)

    # warn if the saved jobs are old
    note = stale_note(jobs)
    if note:
        print(f"{note} To get newer jobs, run: python main.py collect --refresh")


def main():
    # commands: collect [pages] [--refresh], match [--all]
    parser = argparse.ArgumentParser(description="Find the jobs that best match your resume (put it in resumes/).")
    commands = parser.add_subparsers(dest="command", required=True)
    collect_cmd = commands.add_parser("collect", help="get jobs for your resume from JSearch (uses API credits)")
    collect_cmd.add_argument("pages", nargs="?", type=int, default=DEFAULT_PAGES, choices=range(1, MAX_PAGES + 1),
                             metavar="pages",
                             help=f"pages to get, 1-{MAX_PAGES} (each page = up to 10 jobs = 1 credit). Default: {DEFAULT_PAGES}")
    collect_cmd.add_argument("--refresh", action="store_true",
                             help="replace the saved jobs for this resume with new ones (uses credits)")
    match_cmd = commands.add_parser("match", help="show your top 5 job matches and save all ranked jobs to data/results.csv (no API calls)")
    match_cmd.add_argument("--all", action="store_true", dest="show_all",
                           help="show every saved job, best first (default: top 5)")
    args = parser.parse_args()

    try:
        if args.command == "collect":
            collect(find_resume(), args.pages, args.refresh)
        else:
            run_match(args.show_all)
    except (FileNotFoundError, ValueError, requests.RequestException) as e:
        print(f"Error: {e}")
        sys.exit(1)
    # Ctrl+C (or closed input) while running
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()

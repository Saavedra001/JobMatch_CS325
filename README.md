## Job Matcher (CS325 Project 1B)

Finds the 5 job postings that best match your resume.
Jobs come from the JSearch API and are stored locally in SQLite.
Matching runs entirely on your computer. Your resume is never uploaded anywhere.

## Setup (once per computer)

1. Install Python 3.12.
2. Install the libraries:

       python -m pip install -r requirements.txt

3. Copy `.env.example` to `.env` and paste your RapidAPI key in it.
4. Make a `resumes` folder and put your resume in it (`.pdf` or `.txt`).

`.env`, `resumes/` and saved jobs (`data/`) are not in git, so repeat steps 3-4 on each computer.
Tip: copy `data/jobs.db` from your other computer to skip collecting again (saves API credits).

## Commands

    python main.py collect               # get jobs for your resume (1 page = up to 10 jobs = 1 API credit)
    python main.py collect 3             # get 3 pages (up to 30 jobs, 3 credits)
    python main.py collect 3 --refresh   # replace your saved jobs with new ones
    python main.py match                 # show your top 5, save all ranked jobs to results.csv (free)
    python main.py match --all           # show every saved job, best first (free)
    python main.py -h                    # help

Run `collect` once, then `match` as often as you like.
`collect` won't use credits again if jobs for your resume are already saved (use `--refresh` for new ones).

On Mac/Linux, use `python3` instead of `python`.

## Start over (delete all collected jobs)

Do this if you removed your resume or want a clean start. It deletes the saved jobs and `results.csv`:

    rm -f data/jobs.db results.csv                                        # Git Bash / Mac / Linux
    Remove-Item data\jobs.db, results.csv -ErrorAction SilentlyContinue   # PowerShell

Then run `python main.py collect` again (uses API credits).

Added another resume? You don't need to delete anything. If `resumes/` has more than one resume, the program asks which one to use,
and `collect` replaces the old jobs when the new resume needs a different search.
If both resumes give the same search, the saved jobs are reused (add `--refresh` to get new ones).

Jobs data provided by JSearch (OpenWeb Ninja) via RapidAPI.

## Example output

```text
$ python main.py collect
Search: entry level software developer jobs in IL
Got 10 jobs, saved 10 to data/jobs.db (0 duplicates skipped)

$ python main.py match

Your top 5 job matches:

1. Entry Level Implementor/Application Developer
   EBE Technologies | East Moline, IL | Full-time | Posted 2026-11-10
   Matched skills: c#, sql, database
   https://www.linkedin.com/jobs/view/...

2. Entry Level Java/DevOps Developer - Remote
   SynergisticIT | Aurora, IL | Full-time
   Matched skills: python, sql, database, git, full stack
   https://www.monster.com/job-openings/...

...

5. C++ Software Developer - New Grad
   Headlands Technologies LLC | Chicago, IL | Internship
   Matched skills: c++, algorithms, data structures
   https://www.linkedin.com/jobs/view/...

Jobs data provided by JSearch
All 10 ranked jobs saved to results.csv
```

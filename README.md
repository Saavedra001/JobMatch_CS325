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
    python main.py -h                    # help

Run `collect` once, then `match` as often as you like.
`collect` won't use credits again if jobs for your resume are already saved (use `--refresh` for new ones).

On Mac/Linux, use `python3` instead of `python`.

Jobs data provided by JSearch (OpenWeb Ninja) via RapidAPI.

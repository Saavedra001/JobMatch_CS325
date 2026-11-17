# Change log: differences from my Project 1A design

| # | What changed | Why |
|---|---|---|
#1  Job source changed from Adzuna to JSearch by OpenWeb Ninja on RapidAPI. | JSearch pulls listings from Google for Jobs (LinkedIn, Indeed, Glassdoor). Uses one RapidAPI key in `.env` instead of Adzuna's app_id + app_key. 

#2  Results no longer print the match score; they show the matched skills instead (up to 5). | A score like .14 (14%) didn't mean much to the user. Showing the skills that matched explains why the job was picked. The score is still used to rank the jobs. 

#3 The search is built from the resume (role from skill keywords, "entry level" if student, state from the resume's city) instead of the user typing a keyword. | Jobs fit the person automatically. Only role, level and state are sent to the API, never personal info. 

#4 Jobs are replaced on each new search. If the same search is already saved, no API call is made (`--refresh` forces one). Default 3 pages, max 5. | The JSearch free plan has a small monthly limit, so saved jobs are reused instead of collecting daily. 

#5 Jobs older than 30 days show a warning instead of being deleted. | Jobs are replaced on every new search anyway. 

#6 Duplicates: the same title + company + location is also skipped, not just the same id. | The same job is often posted on several sites with different ids. 
#7 More fields saved and shown: location, job type, posted date, source site. | More useful results for the user. |

#8 The resume reader finds the resume in the `resumes/` folder instead of taking a file path. | Easier to run; `resumes/` is in `.gitignore`, so resumes never go to GitHub. 

#9 The resume reader also removes the name and fixes PDF ligatures ("ﬃ" → "ffi"). | More privacy; words like "efficient" were being split. 

#10 Results are also saved to `data/results.csv`. | A 1A "nice to have": view the jobs later. 

import re
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from job_collector import build_query
from job_database import load_jobs, saved_query
from resume_reader import find_resume, read_resume

# skills to look for (written like cleaned text: lowercase, symbols -> spaces, keeps + and #)
SKILLS = [
    # languages
    "python", "java", "c++", "c#", "javascript", "typescript", "php", "sql", "html", "css", "kotlin", "swift",
    # frameworks and libraries
    "react", "angular", "node", "django", "flask", "spring boot", "unity", "pandas", "tensorflow", "pytorch",
    # databases and data tools
    "mysql", "postgresql", "mongodb", "database", "tableau", "power bi", "excel",
    # tools and platforms
    "git", "docker", "kubernetes", "aws", "azure", "linux", "windows", "jenkins",
    # concepts
    "algorithms", "data structures", "object oriented", "full stack", "api", "crud", "agile", "scrum",
    "machine learning", "testing", "devops", "ci cd", "cloud", "cybersecurity", "security clearance",
]


def matched_skills(resume_text, description, limit=5):
    """Skills from SKILLS found in both the resume and the job description (max limit)."""
    resume = f" {resume_text} "
    job = f" {re.sub(r'[^a-z0-9+#]+', ' ', description.lower())} "
    return [s for s in SKILLS if f" {s} " in resume and f" {s} " in job][:limit]


def match_jobs(resume_text, jobs, top_n=5):
    """Return the top_n jobs most similar to the resume, each with a "score" (0-1) and matched "skills"."""
    if not jobs:
        return []

    # resume + job descriptions -> TF-IDF numbers (keep words like c++ and c#)
    texts = [resume_text] + [job["description"] for job in jobs]
    vectors = TfidfVectorizer(stop_words="english", token_pattern=r"[a-z0-9+#]+").fit_transform(texts)

    # compare the resume (row 0) to every job
    scores = cosine_similarity(vectors[0], vectors[1:])[0]

    # best first
    ranked = sorted(zip(jobs, scores), key=lambda pair: pair[1], reverse=True)
    return [
        {**job, "score": round(float(score), 3), "skills": matched_skills(resume_text, job["description"])}
        for job, score in ranked[:top_n]
    ]


# quick test: python src/matcher.py
if __name__ == "__main__":
    try:
        path = find_resume()
        # saved jobs must come from this resume's search
        if saved_query() != build_query(path):
            print("No saved jobs for this resume yet. Run the collector first.")
            sys.exit(1)
        top = match_jobs(read_resume(path), load_jobs())
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    for job in top:
        print(f"{job['score']:.3f}  {job['title']} - {job['company']}")

import sqlite3
from pathlib import Path

# data/jobs.db in the project folder
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs.db"


def connect():
    """Open the database, creating the folder and table if needed."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS jobs ("
        "id TEXT PRIMARY KEY, title TEXT, company TEXT, description TEXT, link TEXT, "
        "location TEXT, job_type TEXT, posted TEXT, query TEXT, source TEXT, collected TEXT)"
    )
    # same title + company + location = same job (posted on another site)
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS same_job "
        "ON jobs (lower(title), lower(company), lower(location))"
    )
    return conn


def save_jobs(jobs):
    """Save a list of job dicts, skipping duplicates. Returns number saved."""
    conn = connect()
    # insert, skip duplicates
    cur = conn.executemany(
        "INSERT OR IGNORE INTO jobs VALUES "
        "(:id, :title, :company, :description, :link, :location, :job_type, :posted, :query, :source, :collected)",
        jobs,
    )
    conn.commit()
    conn.close()
    return cur.rowcount


def load_jobs():
    """Return all saved jobs as a list of dicts."""
    conn = connect()
    jobs = [dict(row) for row in conn.execute("SELECT * FROM jobs")]
    conn.close()
    return jobs


def saved_query():
    """Return the search the saved jobs came from, or None if no jobs are saved."""
    conn = connect()
    row = conn.execute("SELECT query FROM jobs LIMIT 1").fetchone()
    conn.close()
    return row["query"] if row else None


def clear_jobs():
    """Delete all saved jobs. Drops the table so the next save rebuilds it with the current columns."""
    conn = connect()
    conn.execute("DROP TABLE IF EXISTS jobs")
    conn.commit()
    conn.close()

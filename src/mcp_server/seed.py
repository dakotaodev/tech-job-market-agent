"""Seed script — initialize the database and load all seed data.

Usage:
    python -m mcp_server.seed

H-1B data:
    The script downloads the DOL FY2024 H-1B disclosure file on first run and
    caches it at seed_data/h1b_fy2024.csv.  Set H1B_CSV env var to use a
    pre-downloaded file instead.
"""
import os
import urllib.request
from pathlib import Path

from .db import DATABASE, init_db, load_jobs
from .salary import load_h1b_csv

SEED_DIR = Path(__file__).parent / "seed_data"
JOBS_JSON = SEED_DIR / "jobs.json"
H1B_CSV_DEFAULT = SEED_DIR / "h1b_fy2024.csv"

# DOL LCA Disclosure Data — FY2024 (H-1B)
H1B_URL = (
    "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/"
    "LCA_Disclosure_Data_FY2024_Q4.csv"
)

SOFTWARE_TITLE_KEYWORDS = {
    "software", "engineer", "developer", "sre", "devops", "data",
    "machine learning", "backend", "frontend", "platform", "cloud",
    "site reliability", "infrastructure", "full stack", "fullstack",
}

TOP_TECH_EMPLOYERS = {
    "google", "meta", "amazon", "apple", "microsoft", "netflix",
    "stripe", "airbnb", "lyft", "uber", "databricks", "snowflake",
    "confluent", "cloudflare", "figma", "spotify", "shopify",
    "github", "gitlab", "datadog", "twilio", "okta", "palantir",
    "robinhood", "coinbase", "block", "doordash", "pinterest",
    "reddit", "discord",
}


def _download_h1b(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading H-1B FY2024 data → {dest} ...")
    urllib.request.urlretrieve(H1B_URL, dest)
    print("Download complete.")


def load_h1b(csv_path: Path | None = None) -> list[dict]:
    """Load and filter the H-1B dataset.

    Filters to:
    - CASE_STATUS == CERTIFIED
    - Job title containing a software keyword
    - Employer matching one of the top 30 tech companies

    Returns the filtered list of salary records.
    """
    path = Path(os.environ.get("H1B_CSV", "")) if os.environ.get("H1B_CSV") else None
    if path is None or not path.exists():
        path = csv_path or H1B_CSV_DEFAULT
    if not path.exists():
        _download_h1b(path)

    print(f"Parsing H-1B data from {path} ...")
    all_records = load_h1b_csv(str(path))

    filtered = [
        r for r in all_records
        if any(kw in r["job_title"] for kw in SOFTWARE_TITLE_KEYWORDS)
        and any(emp in r["employer_name"] for emp in TOP_TECH_EMPLOYERS)
    ]
    print(f"  Total rows: {len(all_records):,} | Software/top-employer rows: {len(filtered):,}")
    return filtered


def seed(*, skip_h1b: bool = False) -> None:
    """Initialize the database and load all seed data."""
    print(f"Initializing database at {DATABASE} ...")
    init_db()

    print(f"Loading jobs from {JOBS_JSON} ...")
    load_jobs(str(JOBS_JSON))

    import sqlite3
    conn = sqlite3.connect(DATABASE)
    (job_count,) = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()
    conn.close()
    print(f"  Jobs in DB: {job_count}")
    assert job_count >= 150, f"Expected 150+ jobs, got {job_count}"

    if not skip_h1b:
        records = load_h1b()
        assert len(records) >= 40_000, (
            f"Expected 40,000+ H-1B rows after download, got {len(records)}. "
            "The DOL file may have changed URL — update H1B_URL in seed.py."
        )

    print("Seed complete.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the job market database.")
    parser.add_argument(
        "--skip-h1b",
        action="store_true",
        help="Skip H-1B download/validation (useful for offline dev).",
    )
    args = parser.parse_args()
    seed(skip_h1b=args.skip_h1b)

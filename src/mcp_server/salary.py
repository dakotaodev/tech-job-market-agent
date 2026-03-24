import csv
from collections import defaultdict


def _annualize(wage: float, unit: str) -> float | None:
    unit = unit.upper().strip()
    if unit in ("YEAR", "YEARLY", "ANNUAL"):
        return wage
    if unit in ("HOUR", "HOURLY"):
        return wage * 2080
    if unit in ("MONTH", "MONTHLY"):
        return wage * 12
    if unit in ("WEEK", "WEEKLY"):
        return wage * 52
    if unit in ("BI-WEEKLY", "BIWEEKLY"):
        return wage * 26
    return None


def _percentile(sorted_values: list[float], p: float) -> int:
    if not sorted_values:
        return 0
    n = len(sorted_values)
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return int(sorted_values[-1])
    frac = idx - lo
    return int(sorted_values[lo] + frac * (sorted_values[hi] - sorted_values[lo]))


def load_h1b_csv(path: str) -> list[dict]:
    """Parse an H1B disclosure CSV and return a list of normalized salary records.

    Each record contains: job_title, employer_name, worksite_city,
    worksite_state, year, annual_wage.

    The function is tolerant of missing or non-numeric wage values — those
    rows are silently skipped.
    """
    records: list[dict] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Locate wage column — DOL datasets use different names across years
            wage_raw = (
                row.get("WAGE_RATE_OF_PAY_FROM")
                or row.get("PREVAILING_WAGE")
                or row.get("WAGE_FROM")
                or ""
            ).replace(",", "").replace("$", "").strip()

            unit = (
                row.get("WAGE_UNIT_OF_PAY")
                or row.get("PW_UNIT_OF_PAY")
                or "YEAR"
            ).strip()

            try:
                wage = float(wage_raw)
            except ValueError:
                continue

            annual = _annualize(wage, unit)
            if annual is None or annual <= 0:
                continue

            records.append(
                {
                    "job_title": (row.get("JOB_TITLE") or "").strip().lower(),
                    "employer_name": (row.get("EMPLOYER_NAME") or "").strip().lower(),
                    "worksite_city": (row.get("WORKSITE_CITY") or "").strip().lower(),
                    "worksite_state": (row.get("WORKSITE_STATE") or "").strip().upper(),
                    "year": (row.get("YEAR") or row.get("FISCAL_YEAR") or "").strip(),
                    "annual_wage": annual,
                }
            )
    return records


def compute_salary_percentiles(
    records: list[dict],
    *,
    job_title: str | None = None,
    employer_name: str | None = None,
    worksite_state: str | None = None,
    year: str | None = None,
) -> dict:
    """Compute salary percentiles from a list of H1B salary records.

    Filters are applied in combination (AND). Returns a dict with:
      - p25, p50, p75, p90: salary percentiles (USD annual)
      - total_records: number of records used
      - by_title: {title: p50} for the top titles in the filtered set
      - by_employer: {employer: p50} for employers in the filtered set
      - by_location: {state: p50} for states in the filtered set
      - by_year: {year: p50} across calendar years in the filtered set
    """
    filtered = records

    if job_title:
        needle = job_title.lower()
        filtered = [r for r in filtered if needle in r["job_title"]]

    if employer_name:
        needle = employer_name.lower()
        filtered = [r for r in filtered if needle in r["employer_name"]]

    if worksite_state:
        needle = worksite_state.upper()
        filtered = [r for r in filtered if r["worksite_state"] == needle]

    if year:
        filtered = [r for r in filtered if r["year"] == year]

    wages = sorted(r["annual_wage"] for r in filtered)

    if not wages:
        return {
            "p25": 0,
            "p50": 0,
            "p75": 0,
            "p90": 0,
            "total_records": 0,
            "by_title": {},
            "by_employer": {},
            "by_location": {},
            "by_year": {},
        }

    def _group_p50(key: str) -> dict[str, int]:
        buckets: dict[str, list[float]] = defaultdict(list)
        for r in filtered:
            buckets[r[key]].append(r["annual_wage"])
        return {k: _percentile(sorted(v), 50) for k, v in buckets.items()}

    return {
        "p25": _percentile(wages, 25),
        "p50": _percentile(wages, 50),
        "p75": _percentile(wages, 75),
        "p90": _percentile(wages, 90),
        "total_records": len(wages),
        "by_title": _group_p50("job_title"),
        "by_employer": _group_p50("employer_name"),
        "by_location": _group_p50("worksite_state"),
        "by_year": _group_p50("year"),
    }

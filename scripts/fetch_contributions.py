"""
fetch_contributions.py
Scrape the public contribution calendar HTML fragment GitHub serves
(no token needed) and write derived stats to data/contributions.json.

Usage:
    python scripts/fetch_contributions.py
Writes:
    data/contributions.json
"""
import json
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = "AnupojuRohit"  # <-- replace with your GitHub username
URL = f"https://github.com/users/AnupojuRohit/contributions"
OUTPUT_JSON = "data/contributions.json"


def fetch():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day"):
        date = cell.get("data-date")
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
        if date is None:
            continue
        days.append({
            "date": date,
            "level": int(level) if level is not None else 0,
            "count": int(count_attr) if count_attr is not None else 0,
        })

    if not days:
        print("No contribution cells found -- GitHub may have changed markup.", file=sys.stderr)

    days.sort(key=lambda d: d["date"])
    stats = compute_stats(days)

    with open(OUTPUT_JSON, "w") as f:
        json.dump({"days": days, "stats": stats}, f, indent=2)
    print(f"Wrote {OUTPUT_JSON} ({len(days)} days)")


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # current streak: consecutive days with count > 0, ending today (or most recent day)
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


if __name__ == "__main__":
    fetch()

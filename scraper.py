"""
SIGNAL scraper — pulls hackathons, internships, and jobs from free public
APIs, filters engineering roles down to electrical / automation / oil & gas
/ power / instrumentation relevance, and writes docs/data.json.

Runs on a schedule via GitHub Actions (see .github/workflows/scrape.yml).
No API keys required — every source below is free and unauthenticated.
"""
import json
from datetime import datetime, timezone

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (SignalRadar/1.0; personal opportunity tracker)"}

# Keywords that define "relevant" for Linus: electrical engineering,
# industrial automation, oil & gas, power systems.
KEYWORDS = [
    "electrical", "electrical engineer", "instrumentation", "automation",
    "scada", "plc", "power system", "power systems", "power plant",
    "oil and gas", "oil & gas", "upstream", "downstream", "petroleum",
    "control system", "controls engineer", "process engineer",
    "renewable energy", "solar", "grid", "substation", "transmission",
    "mechatronics", "commissioning engineer", "hse engineer",
    "maintenance engineer", "energy engineer", "field engineer",
    "graduate trainee", "graduate engineer", "industrial engineer",
]


def matches(*parts):
    text = " ".join(p for p in parts if p).lower()
    return any(k in text for k in KEYWORDS)


def fetch_remotive():
    """Remotive: free API, CORS-enabled, no key. Search pre-filtered server-side."""
    out = []
    try:
        r = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": "electrical engineer"},
            headers=HEADERS, timeout=20,
        )
        r.raise_for_status()
        for j in r.json().get("jobs", []):
            out.append({
                "title": j.get("title"),
                "org": j.get("company_name"),
                "location": j.get("candidate_required_location") or "Remote",
                "type": j.get("job_type") or "",
                "url": j.get("url"),
                "tag": "Internship" if "intern" in (j.get("title") or "").lower() else "Job",
                "source": "Remotive",
            })
    except Exception as e:
        print("Remotive failed:", e)
    return out


def fetch_arbeitnow():
    """Arbeitnow job board API: free, no key, broad international listings."""
    out = []
    try:
        r = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=20)
        r.raise_for_status()
        for j in r.json().get("data", []):
            title = j.get("title", "")
            tags = " ".join(j.get("tags", []) or [])
            if not matches(title, tags):
                continue
            is_intern = "intern" in (title + tags).lower()
            out.append({
                "title": title,
                "org": j.get("company_name"),
                "location": j.get("location") or "Remote",
                "type": "Remote" if j.get("remote") else "On-site",
                "url": j.get("url"),
                "tag": "Internship" if is_intern else "Job",
                "source": "Arbeitnow",
            })
    except Exception as e:
        print("Arbeitnow failed:", e)
    return out


def fetch_jobicy():
    """Jobicy: free remote-jobs API, no key."""
    out = []
    try:
        r = requests.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": 50}, headers=HEADERS, timeout=20,
        )
        r.raise_for_status()
        for j in r.json().get("jobs", []):
            title = j.get("jobTitle", "")
            industry = j.get("jobIndustry", "")
            industry = " ".join(industry) if isinstance(industry, list) else str(industry)
            if not matches(title, industry):
                continue
            out.append({
                "title": title,
                "org": j.get("companyName"),
                "location": j.get("jobGeo") or "Remote",
                "type": j.get("jobType", ""),
                "url": j.get("url"),
                "tag": "Internship" if "intern" in title.lower() else "Job",
                "source": "Jobicy",
            })
    except Exception as e:
        print("Jobicy failed:", e)
    return out


def fetch_devpost():
    """Devpost hackathons API. Blocked by CORS in-browser, fine server-side."""
    out = []
    try:
        r = requests.get(
            "https://devpost.com/api/hackathons",
            params={"status[]": "open"}, headers=HEADERS, timeout=20,
        )
        r.raise_for_status()
        for h in r.json().get("hackathons", [])[:30]:
            loc = h.get("displayed_location", {}) or {}
            themes = h.get("themes") or []
            out.append({
                "title": h.get("title"),
                "org": "Devpost",
                "location": loc.get("location", "Online"),
                "type": themes[0].get("name", "") if themes else "",
                "url": h.get("url"),
                "tag": "Hackathon",
                "source": "Devpost",
            })
    except Exception as e:
        print("Devpost failed:", e)
    return out


def nigeria_board_links():
    """
    No free public API exists for Jobberman, MyJobMag, or Hot Nigerian Jobs,
    and scraping them isn't something this project does. Instead: direct,
    pre-filled search links so one click gets straight to relevant results.
    """
    q = "electrical+engineer+OR+automation+OR+instrumentation+OR+oil+and+gas"
    return [
        {
            "title": "Search: Electrical / Automation / Oil & Gas roles",
            "org": "Jobberman Nigeria",
            "location": "Nigeria",
            "type": "Search link",
            "url": f"https://www.jobberman.com/jobs?q={q}",
            "tag": "Job",
            "source": "Jobberman",
        },
        {
            "title": "Search: Electrical / Automation / Oil & Gas roles",
            "org": "MyJobMag",
            "location": "Nigeria",
            "type": "Search link",
            "url": "https://www.myjobmag.com/search/jobs?q=electrical+engineer",
            "tag": "Job",
            "source": "MyJobMag",
        },
        {
            "title": "Search: Electrical / Automation / Oil & Gas roles",
            "org": "Hot Nigerian Jobs",
            "location": "Nigeria",
            "type": "Search link",
            "url": "https://www.hotnigerianjobs.com/hotjobs/search/?q=electrical+engineer",
            "tag": "Job",
            "source": "Hot Nigerian Jobs",
        },
        {
            "title": "Search: NYSC PPA-eligible engineering roles",
            "org": "NGCareers",
            "location": "Nigeria",
            "type": "Search link",
            "url": "https://ngcareers.com/jobs?q=electrical+engineer",
            "tag": "Job",
            "source": "NGCareers",
        },
    ]


def main():
    remotive = fetch_remotive()
    arbeitnow = fetch_arbeitnow()
    jobicy = fetch_jobicy()
    devpost = fetch_devpost()
    ng_links = nigeria_board_links()

    combined_jobs_pool = remotive + arbeitnow + jobicy + ng_links
    internships = [j for j in combined_jobs_pool if j["tag"] == "Internship"]
    jobs = [j for j in combined_jobs_pool if j["tag"] == "Job"]

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hackathons": devpost,
        "internships": internships,
        "jobs": jobs,
    }

    with open("docs/data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(
        f"hackathons={len(devpost)} internships={len(internships)} jobs={len(jobs)} "
        f"@ {data['generated_at']}"
    )


if __name__ == "__main__":
    main()

# SIGNAL — Opportunity Radar

A personal dashboard that tracks hackathons, internships, and jobs — filtered
for electrical engineering / industrial automation / oil & gas relevance.
Runs entirely on free tiers: GitHub Actions (scraping + scheduling), GitHub
Pages (hosting). No servers, no paid APIs, no credit card.

## How it works

- `scraper.py` pulls from free public APIs (Remotive, Arbeitnow, Jobicy,
  Devpost) and filters results against an engineering keyword list.
- `.github/workflows/scrape.yml` runs the scraper twice a day and commits
  the fresh `docs/data.json`.
- `docs/index.html` is the dashboard itself — reads `data.json` and renders it.
  GitHub Pages serves this folder as your live site.

## Setup (10 minutes, all free)

1. **Create a GitHub account** if you don't have one: github.com/join

2. **Create a new repository**
   - Go to github.com/new
   - Name it `signal-radar` (or anything you like)
   - Set it to **Public** (required for free GitHub Actions minutes to be unlimited)
   - Don't initialize with a README (you already have one)

3. **Upload these files**
   - On the new repo page, click "uploading an existing file"
   - Drag in the whole folder structure exactly as given:
     ```
     scraper.py
     requirements.txt
     README.md
     .github/workflows/scrape.yml
     docs/index.html
     docs/data.json
     ```
   - Commit directly to `main`

4. **Turn on GitHub Pages**
   - Repo → Settings → Pages
   - Under "Build and deployment" → Source: **Deploy from a branch**
   - Branch: `main`, folder: `/docs` → Save
   - GitHub gives you a URL like `https://yourusername.github.io/signal-radar/`
     — that's your live site.

5. **Run the scraper once manually** (don't wait for the schedule)
   - Repo → Actions tab → click "Refresh opportunity data" → "Run workflow"
   - Wait ~30 seconds, refresh your Pages URL — cards should appear

6. **Done.** It now refreshes itself twice a day automatically. Bookmark the
   Pages URL, or add it to your phone's home screen for an app-like feel.

## Customizing the keyword filter

Open `scraper.py`, edit the `KEYWORDS` list near the top. Add or remove terms
to widen or narrow what counts as "relevant." Commit the change — the next
scheduled run picks it up automatically.

## Changing the refresh schedule

Edit the `cron` line in `.github/workflows/scrape.yml`. Format is
`minute hour day month weekday`, all in UTC. E.g. `"0 */4 * * *"` = every 4 hours.

## What's next (Phase 2+)

- **Notifications**: a step in the workflow that diffs new data.json against
  the previous version and pings a free Telegram bot when something new
  matches — no polling required on your side.
- **Nigeria-specific scraping**: Jobberman/MyJobMag/Hot Nigerian Jobs don't
  have public APIs, so real listings (not just search links) would need a
  lightweight scraper — doable, but worth checking each site's terms first.
- **History & dedup**: move from a single overwritten `data.json` to a small
  free database (Supabase) so you can see "new since yesterday" instead of
  just the current snapshot.

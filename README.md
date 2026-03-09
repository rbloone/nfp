# Neste Latvia fuel tracker with GitHub Actions

This repo scrapes daily fuel prices from Neste Latvia and stores them in `data/fuel_prices.csv`.

It also includes a tiny chart page in `docs/index.html`, which you can publish with GitHub Pages.

## What you get

- daily scrape with GitHub Actions
- CSV history committed into your repo
- simple chart page on GitHub Pages
- manual "Run workflow" button too

## Files

- `scraper.py` — fetches and parses the prices
- `.github/workflows/scrape.yml` — runs once a day and commits CSV changes
- `data/fuel_prices.csv` — your history
- `docs/index.html` — browser chart

## Setup

### 1) Create a GitHub repo

Create a new repo and upload these files.

### 2) Enable Actions

Push the repo to GitHub. The workflow file must be on your default branch.

### 3) Enable GitHub Pages

In your repo:
- Settings → Pages
- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/docs**

Then your chart page will be published.

### 4) Run it once manually

Go to:
- Actions → `Scrape Neste fuel prices`
- `Run workflow`

That confirms everything works before the daily schedule kicks in.

## Schedule

The workflow uses:

```yaml
- cron: "5 7 * * *"
```

GitHub Actions cron is **UTC**.
That means:
- **09:05** in Latvia during winter time (EET)
- **10:05** in Latvia during summer time (EEST)

Change that if you want a different hour.

## Local test

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scraper.py
```

## Notes

- The Neste page says prices are informational, may change several times per day, and are not updated on weekends or holidays.
- This scraper is built for the current page structure. If Neste redesigns the page, the parser may need a small update.
- The workflow commits only when `data/fuel_prices.csv` changed.

## Nice upgrades later

- add a 7-day / 30-day average
- export a PNG chart
- add email or Telegram alerts when prices drop
- switch from CSV to SQLite

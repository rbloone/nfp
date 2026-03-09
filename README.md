# Neste Latvia fuel price tracker

This repo scrapes daily fuel prices from https://www.neste.lv/lv/content/degvielas-cenas
and publishes a simple chart on GitHub Pages.

## Setup

1. Create a new GitHub repo.
2. Upload all files from this ZIP.
3. Commit to your default branch, usually `main`.
4. In GitHub, open **Settings → Pages**.
5. Set:
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
6. Open **Actions** and run **Scrape Neste fuel prices** once with **Run workflow**.
7. Wait for the workflow to finish, then open your Pages URL.

## Notes

- GitHub Actions cron uses UTC.
- The workflow is set to run at `07:05 UTC` every day.
- The CSV is inside `docs/` on purpose, because GitHub Pages only serves files from the published folder.

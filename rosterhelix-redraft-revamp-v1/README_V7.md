# FourthDown Analytics Fantasy V7

## Local run

1. `python scripts/update_data.py --season 2026` (requires internet; downloads nflverse current-season weekly offense CSV).
2. `python scripts/backtest.py` (optional historical model evaluation).
3. `python server.py` and visit http://localhost:8000.

If the data provider changes the current season URL, override with `--source /path/to/weekly.csv` or `FOURTHDOWN ANALYTICS_STATS_URL=https://...`.

## Backend endpoints
- `GET /api/health` — health and dataset presence
- `GET /api/status` — data provenance and last update
- `GET /api/players` — player search list
- `GET /api/projections?week=8&scoring=ppr` — five-game weighted baseline projections using only games before the requested week. Also accepts `half` and `standard`.

## Daily automation
`.github/workflows/update-stats.yml` runs daily at 12:30 UTC when the project is pushed to a GitHub repository with Actions enabled and permissions allowing workflow commits. It intentionally fails rather than replacing good data if the upstream feed is unavailable. It does not run automatically from a downloaded ZIP.

## Coverage and limitations
- NFLverse current stats_player weekly offense: public source; not live play-by-play. Actual data will only appear after a successful network sync.
- Snap share, routes, and injuries are **not** included in this free weekly offense feed. The UI must not claim those are populated. nflverse PFR snap-count data is a separate feed; participation is not refreshed in-season and injury feed is unavailable for recent seasons. These require separate ingestion/licensing review.
- Opponent adjustment is not wired into the `/api/projections` baseline. Existing Matchup Lab remains a separate import/report feature.
- The local HTTP server is for development only; do not expose it publicly without authentication, rate limits, secure hosting and a production-grade deployment.
- Attribution: NFL data via nflverse, https://github.com/nflverse/nflverse-data. Review each dataset's license before commercial use, particularly FTN data (CC BY-SA).

## Deployment
Push the source to GitHub, enable Actions, run the workflow manually once, and verify `data/metadata.json`. Host the app using a Python-capable server for API endpoints or serve static files from a static host (API endpoints will not be available on static hosting). Keep source attributions visible.

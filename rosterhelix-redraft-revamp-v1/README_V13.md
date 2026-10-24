# FourthDown Analytics Fantasy V13 — Bulk Historical Sync

## Start locally

```bash
python server.py
```

Open http://127.0.0.1:8000, choose **Import data**, select a season range, and click **Download seasons**. This uses the publicly available NFLverse `stats_player_week_{season}.csv` release files over HTTPS. Downloads require network access; this package does **not** include verified NFL datasets.

Alternatively:

```bash
python scripts/sync_history.py --start 2020 --end 2025
```

All seasons in the requested range are downloaded and validated before any records are merged into `data/history_player_stats.csv`. Existing player-games are updated by `(season, week, player_id)` and the newest season is copied to `data/player_stats.csv` for the advanced analytics tools. Historical matchups derive opponent-position observed totals from imported player games.

**Important:** Historical records depend on the source release availability and schema. Missing seasons or connectivity failures stop the entire batch. Historical matchup totals are observed fantasy points allowed, not necessarily predictive rankings. There is no verified live injury feed, and routes/snaps are not available from this importer.

## API

`POST /api/history/sync?start=2020&end=2025` downloads the range. This can take minutes; the endpoint is intended only for local development. Other endpoints from V12 remain available.

## Security and deployment

The development server now binds to `127.0.0.1` rather than all interfaces. **Do not expose the sync endpoint on a public server.** It performs remote downloads and writes files without authentication. Before public deployment, restrict it to an authenticated administrative job, add rate limits and request origin protection, and move persistence to a database. The development server should not be used as a public production server.

## Tests

```bash
python -m unittest discover -s scripts -p 'test_*.py' -q
```

32 automated tests passed in this build. They are unit tests, **not** a successful live NFLverse import or an end-to-end browser test. Data licensing and permitted commercial use should be verified with the relevant publishers before monetizing FourthDown Analytics.

# FourthDown Analytics Fantasy V8 — Free-data defensive matchup integration

## Run locally

```bash
python scripts/update_data.py --season 2026
python scripts/build_defense.py
python scripts/build_matchups.py
python scripts/backtest.py
python -m unittest discover -s scripts -p 'test_*.py'
python server.py
```

Visit http://localhost:8000. The frontend automatically attempts to load synced weekly player statistics and `data/matchups.json`; when either is missing, the interface remains in demo mode or reports the missing report. API routes include `/api/health`, `/api/status`, `/api/players`, `/api/projections?week=8&scoring=ppr`, and `/api/matchups`.

## What V8 actually adds

- Preserves `opponent_team` in imported nflverse player-game rows.
- Aggregates **observed** fantasy PPR points allowed by each defense to QBs, RBs, WRs and TEs. For WR/RB/TE, all eligible players against that defense are summed, not treated as individual matchup scores.
- Computes an observed same-week league average for each position, then shrinks/caps the opponent multiplier using strictly earlier games.
- Writes `data/defense_allowed.csv` and `data/matchups.json` for the existing Matchup Lab.
- Adds `/api/matchups` and updates the GitHub Actions refresh workflow to build both datasets daily.
- Eight Python tests pass, including aggregation and lookahead-leakage tests.

## Critical limitations

**Not a validated upcoming-player projection.** The Matchup Lab reports how a defense has performed against a position historically. The website does not automatically identify each player's upcoming opponent, and the API's player projections remain historical weighted-five-game baselines with `matchup_adjusted: false`. Avoid advertising opponent-adjusted player predictions until a verified schedule is joined to player teams and the adjustment is backtested.

Data is not live until the importer successfully downloads nflverse stats_player weekly CSV. The upstream feed may change, be unavailable, or omit `opponent_team`; the defensive build intentionally fails rather than fabricating data. There is no verified live injury, route participation, or weather feed. Free dataset availability does **not** establish permission for commercial redistribution; review upstream licensing before monetization.

## GitHub and hosting

GitHub is recommended for code history, backups, and running the included scheduled Actions workflow, but it is **not required** for local development. GitHub Actions does not host the Python API; use a Python-capable deployment service separately. Upload the project to a repository, enable Actions, trigger the workflow once, and inspect the generated `data/metadata.json`, `data/defense_allowed.csv`, and `data/matchups.json`. Do not treat a configured workflow as a verified successful refresh.

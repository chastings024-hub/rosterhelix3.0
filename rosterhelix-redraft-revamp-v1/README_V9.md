# FourthDown Analytics Fantasy V9 — Schedule-aware matchup projections

## Quick start

```bash
python scripts/update_data.py --season 2026
python scripts/build_schedule.py --season 2026
python scripts/build_defense.py
python scripts/build_matchups.py
python scripts/backtest.py
python -m unittest discover -s scripts -p 'test_*.py'
python server.py
```

Open http://localhost:8000 and use **Upcoming Week Forecasts**. The API endpoint `/api/projections?week=8&scoring=ppr` now includes upcoming opponent, baseline, defensive multiplier, sample size and projected points. `/api/schedule?week=8` exposes imported scheduled games. The GitHub Actions workflow is configured to import schedules each day as well as player and defensive stats.

### Free data inputs

- Weekly player statistics: nflverse `stats_player` release (existing V7/V8 importer).
- NFL schedule: `https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv`. If upstream changes or lacks the selected season, importer fails safely instead of inventing games. Override using `--source /path/to/games.csv`.
- Defense: aggregated from observed weekly player fantasy points against opponents; requires valid `opponent_team` in source stats.

### Important limitations

These are **experimental, uncalibrated projections** based on weighted recent fantasy points and a shrunk defensive points-allowed ratio, not a validated winning strategy. The defense adjustment is derived from aggregate PPR points allowed even for half/standard scoring. No live injury, routes, snap share or weather integration. Team names from schedules and player stats must match; missing mappings may appear as unconfirmed/bye and should not be treated as verified bye weeks. No live network refresh has been verified in this build. This local API is not hardened for public hosting: add authentication/rate limits, caching, security headers, structured monitoring and production hosting before public launch. Review nflverse dataset license/terms before commercial redistribution.

Run tests before deploying. GitHub Actions configuration alone does not confirm a successful scheduled run or deploy the Python API.

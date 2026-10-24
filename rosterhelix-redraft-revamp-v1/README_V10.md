# FourthDown Analytics Fantasy V10 — Decision Lab

## Run locally

1. Python 3.10+ is required; no external Python packages are required.
2. Run `python scripts/update_data.py --season 2026` to download the weekly NFLverse dataset (requires internet).
3. Run `python scripts/build_schedule.py --season 2026` to download the schedule (requires internet).
4. Run `python scripts/build_defense.py` and `python scripts/build_matchups.py` to derive defensive matchups.
5. Run `python server.py` and open `http://localhost:8000`.
6. Open the **V10 Decision Lab**, choose week/scoring and press **Run V10 analysis**.
7. Run `python -m unittest discover -s scripts -p 'test_*.py'` to test the models.

## New API routes

- `GET /api/opportunity?week=7&scoring=ppr` — observed targets, carries, receptions and opportunities, with missing advanced metrics as null.
- `GET /api/ros?week=7&scoring=ppr` — future scheduled games, fixed pre-week baseline, defense factors based on earlier observations.
- `GET /api/accuracy?week=7&scoring=ppr` — walk-forward baseline error, overall/by position/by week.
- `GET /api/projections?week=7&scoring=ppr&scenario_status=questionable&availability=0.75` — manual what-if availability, not a medical forecast.

## Limitations and safety

The app does not fetch verified live injury reports, snap share, route participation or target share. The scenario probability is a user-supplied assumption; injury status is not sourced. Missing future schedule data are flagged and excluded from totals, not treated as confirmed byes. ROS projections hold each player's historical form fixed at the selected week and do not simulate weekly usage, new injuries, waiver pickups or playoff lineups. Trade simulator uses fixed starter slots, not an optimized weekly schedule. The accuracy report measures the historical baseline, **not** the injury, defense-adjusted, or ROS model. The free upstream data sources may have licensing and availability restrictions for commercial use. No public hosting or live download was verified in this environment.

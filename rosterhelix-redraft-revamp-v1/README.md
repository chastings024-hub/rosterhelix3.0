# FourthDown Analytics Fantasy V4 — advanced analytics

Optional enrichment CSV columns: `player_id,season,week,snap_share,route_participation,opponent,matchup_factor,injury_status`. Player IDs must match imported weekly stats. Snap and route percentages can be fractions (0.8) or percentages (80). Matchup factor is user-supplied, clamped to 0.65–1.35 and applied as a multiplicative scenario factor, **not an independently derived defensive strength model**. Injury statuses are displayed but do not automatically change projections. Missing participation values show N/A. Two-for-one trade values include a selectable replacement player or estimated replacement baseline. The model remains unvalidated and historical; do not treat as betting or high-confidence advice.

# FourthDown Analytics Fantasy V3 — NFL data pipeline

This is a local web prototype, not a hosted real-time fantasy product. The app supports three tools: trade comparison, start/sit baselines and player analytics. All historical data comes from an explicit user import or a local sync job; the fallback is fictional demo data.

## Quick start

From the `fourthdown-analytics-fantasy` directory:

```bash
python scripts/update_data.py --season 2026
python -m http.server 8000
```

Open http://localhost:8000 and click **Load synced NFL data**. The script fetches nflverse's public weekly player-statistics CSV and writes `data/player_stats.csv` plus `data/metadata.json`. If the upstream release URL or schema changes, pass `--source /path/to/weekly.csv` or `--source https://...`. Verify dataset redistribution/commercial-use permissions before publishing.

To refresh automatically, schedule the same Python command on a server or GitHub Actions workflow (see `.github/workflows/update-stats.yml`). A hosted frontend needs the generated CSV deployed alongside it. Opening `index.html` directly via `file://` may block fetch requests; use an HTTP server.

## Model caveats

The app deliberately uses **historical baseline estimates**, not real-time opponent-aware predictions. The last five games are weighted by position-specific exponential decay (QB .86, RB .74, WR .78, TE .82). No historical training/backtesting has been performed to validate these decay rates. ±1 historical standard deviation is **not** a confidence or calibrated prediction interval. Trade scores are heuristics, not rest-of-season valuations; multi-player trades do not account for replacement slots. The CSV does not supply snap share, routes, injuries, opponent adjustments, weather, or future matchup information; those fields must remain unavailable rather than fabricated. Selecting an analysis week excludes that week and all future games to reduce lookahead bias.

## Next production requirements

Licensed participation and injury feeds, game/opponent joins, automated data quality tests, temporal cross-validation against held-out seasons, position-specific opportunity models, lineup-aware trade value and proper server-side data storage.

## V5 Model Lab

Run `python scripts/test_models.py` for unit checks, `python scripts/update_data.py --season 2026` to import the public historical weekly feed (network required), and `python scripts/backtest.py` to generate `data/backtest.json`. Serve via `python -m http.server 8000`, load synced data and open **Model Lab** to view backtest results. The automated workflow now generates the backtest report. The Model Lab also includes a limited same-position roster swap estimator and a metric coverage audit. It does **not** connect to a licensed live snap, route, injury, or defensive data feed. Weekly source CSV and optional enrichment remain the only supported inputs. No statistical confidence claims should be inferred from MAE/RMSE.

## V6 — Opponent Matchup Lab

Generate optional matchup factors from an independently sourced defensive-statistics CSV:

```bash
python scripts/matchup_engine.py --input /path/to/defense.csv --season 2026 --week 9
python -m unittest discover -s scripts -p 'test_*.py' -v
python -m http.server 8000
```

Input schema: `season,week,defense_team,position,points_allowed,league_avg_points` (one team-position-week record). `points_allowed` and `league_avg_points` must be measured in the same scoring format and aggregation level. Defensive fantasy points allowed should be **total fantasy points allowed to that position by the defense in that game**; league average must be calculated comparably. The engine excludes records on or after the forecast week, averages up to 12 prior observations, shrinks to neutral for low sample sizes, and caps factors at 0.80–1.20. It writes `data/matchups.json`. Open the Matchup Lab and click **Load matchup report** (or upload the JSON manually). This report is **diagnostic only**; it does not silently alter trade or start/sit recommendations. Doing so safely requires verified upcoming opponents, injury data, and validated position-level projections. This release does not claim a licensed or real-time feed.

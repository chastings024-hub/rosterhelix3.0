# FourthDown Analytics Fantasy V14 — Historical Model Comparison

## Run locally

```bash
python server.py
```

Visit http://127.0.0.1:8000, open **Import data**, and select **Download seasons** (internet required), or upload NFLverse stats_player CSV files. Then open **Model accuracy** and click **Compare models**.

## What it measures

V14 compares two approaches on the same historical player-games:

1. Baseline: recency-weighted last five prior player games (at least two required).
2. Matchup adjusted: same baseline multiplied by a shrunk defensive-points-allowed factor, using ONLY completed earlier weeks.

Results include MAE, RMSE, bias, position breakdowns, and the number of forecasts with actual non-neutral defensive adjustments. Lower MAE is better; positive MAE improvement means the matchup model reduced error. Historical results do not establish future accuracy.

The **Model Accuracy** tab calls `GET /api/validation/compare?scoring=ppr` (also `half` and `standard`). CLI equivalent:

```bash
python scripts/compare_models.py --output data/model_comparison.json
```

## Known limitations

- The environment used to package this version cannot resolve the NFLverse host. No successful live download or real-season benchmark is claimed.
- Imported records have not been independently verified for completeness or authenticity.
- The defense comparison uses fantasy points allowed aggregated from the imported offensive game logs; missing player rows bias defensive totals.
- Defensive matchup adjustment is a heuristic, not a calibrated probability model.
- The comparison does not model injuries, routes, weather, betting lines, or lineup decisions.
- V14 is a local development server, not an authenticated public deployment.

## Testing

```bash
python -m unittest discover -s scripts -p 'test_*.py' -q
```

Tests cover leakage prevention, paired sample accounting, scoring variations, and existing import/projection logic.

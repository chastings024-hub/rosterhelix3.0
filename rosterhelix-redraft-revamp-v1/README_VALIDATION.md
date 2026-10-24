# FourthDown Analytics — Real NFL data validation (V11)

This package adds a reproducible player-week data audit and walk-forward accuracy report. **No real dataset was successfully downloaded in this build environment**. There is no claim of measured real-world accuracy yet.

## Validate real NFLverse data

```bash
python scripts/update_data.py --season 2025
python scripts/validate_real_data.py --input data/player_stats.csv --season 2025 --source nflverse-import
```

The importer fetches `https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2025.csv`. Use `--source /path/to/stats_player_week_2025.csv` on the importer to supply a manually downloaded copy if networking is restricted. The validation report is written to `data/validation_report.json`. The source label is a user-supplied provenance assertion, **not** independent cryptographic verification of upstream authenticity. SHA-256 enables subsequent file comparisons.

The audit checks schema, invalid values, season/week, duplicate player-week keys, position coverage and a previous-games-only baseline MAE/RMSE/bias. It fails on invalid or duplicate rows, or zero evaluated games. The backtest does not validate matchup adjustments, injury assumptions, or trade recommendation quality.

Run the full test suite:

```bash
python -m unittest discover -s scripts -p 'test_*.py'
```

## Known limitations

- 2026 NFLverse player stats may be delayed or unavailable at a given URL; check release status.
- Historical data changes can affect results; save the input hash with the report.
- Historical walk-forward prediction uses only a player's earlier games, but does not include explicit publication timestamps for each observation. A real deployment should enforce game completion/publication cutoffs.
- Model comparisons should use identical player-week samples, scoring settings, and a frozen evaluation period.
- This is not an injury or matchup-model validation, and a small MAE does not imply actionable trade or start/sit superiority.
- Credit nflverse and review its data licenses before commercial deployment.

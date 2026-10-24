# FourthDown Analytics Fantasy V12 — Historical Data Center

## Start

```bash
cd fourthdown-analytics-fantasy
python server.py
```

Open `http://localhost:8000` (not a `file://` preview). The simplified homepage has Player history, Defense matchups, and Import data. The earlier full trade, start/sit, and model lab interface is preserved at `/analytics.html`.

## Import real NFL history

Use **Import data** on the homepage. Supported formats:

- **NFLverse weekly `stats_player` CSV:** choose the NFLverse format and enter the corresponding season. Import one season at a time; multiple imports merge.
- **Normalized FourthDown Analytics CSV:** requires `player_id,player_name,position,season,week,fantasy_points_ppr`. Recommended additional columns: `recent_team,opponent_team,receptions,receiving_targets,rushing_attempts`. A downloadable template is available in the interface.

Source: https://github.com/nflverse/nflverse-data/releases/tag/stats_player

The import runs on your local Python server. A 35 MB per-file limit applies. Rows are deduplicated by `(season,week,player_id)`. Stored history is `data/history_player_stats.csv`; `data/player_stats.csv` is updated to the newest imported season for compatibility with older tools. Importing replaces matching player-game records, and files should be backed up before large merges. Uploads are not independently verified as authentic NFL statistics.

## Historical matchup analysis

The matchup table sums imported PPR fantasy points across all observed QB/RB/WR/TE player-games against a given defense per week. **This is an observed total, not a normalized predictive strength score.** Missing opponent IDs mean the matchup is not included. Season, opponent, position, and player filters are available.

## API

- `GET /api/history/summary` — coverage
- `GET /api/history?player=...&season=2025&position=WR&opponent=DAL&limit=500` — player games
- `GET /api/history/matchups?season=2025&opponent=DAL&position=WR` — defense-position weeks
- `POST /api/history/import?format=canonical` — CSV bytes
- `POST /api/history/import?format=nflverse&season=2025` — nflverse CSV bytes

**Security:** This is a local development server with unauthenticated import access and permissive CORS. Do **not** expose it directly to the public internet. Add authentication, CSRF/origin protections, rate limits, and an external database before public deployment.

## Tests

```bash
python -m unittest discover -s scripts -p 'test_*.py' -q
```

Data accuracy depends on the source CSV. No live feed has been verified here.

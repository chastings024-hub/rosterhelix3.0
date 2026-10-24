# FourthDown Analytics V15.1 sync troubleshooting

1. Start `py server.py` in the extracted folder, then open http://127.0.0.1:8000.
2. Select Import and try a single completed season, e.g. 2024 through 2024.
3. If it fails, read the detailed message now displayed in the interface. DNS/firewall errors require network troubleshooting; HTTP 404 means that asset is unavailable.
4. Manual fallback: visit https://github.com/nflverse/nflverse-data/releases/tag/stats_player and download `stats_player_week_2024.csv`. Under Upload CSV choose **NFLverse stats_player weekly CSV**, enter 2024, select the downloaded file, then Import CSV.
5. Don't download the older frozen `player_stats` release. Do not delete existing data.

No live external download has been verified in this environment.

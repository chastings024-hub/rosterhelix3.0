# FourthDown Analytics V32 — Complete fantasy research workspace

FourthDown Analytics is the selected final project name. This release includes the roster, player research, decision center, and model tools from the earlier versions. No NFL or team logos are used.

## Windows setup
1. Extract the ZIP; open the `fourthdown-analytics-v32` folder in File Explorer.
2. Click the address bar, type `cmd`, and press Enter.
3. Run `py server.py` (or `python server.py`).
4. Visit `http://127.0.0.1:8000`.
5. Go to **Data Manager** to import a trusted NFLverse weekly CSV, or test a single-season sync.
6. Go to **Player Profiles** to browse historical stats. In **My Team**, search and add players, set league lineup slots and scoring, and click **Save roster**.
7. Open the dashboard and select **Refresh my team analysis** to see a historical-form starting lineup.

## Upgrade / retain your data
Stop the old server before launching the new one. To retain previous historical imports, copy `data/history_player_stats.csv`, `data/player_stats.csv`, and `data/metadata.json` from the old extracted folder to the same paths in this folder. Do not overwrite your original files until you've backed them up. FourthDown Analytics stores the saved roster in `data/workspace.json`; copy that file when upgrading again.

## What was added
- Local single-league roster save and edit with player ID-based selection and server-side validation.
- Player research profiles with imported weekly game logs, recent and season PPR averages, usage averages, and volatility.
- Personalized dashboard decision center, using recent historical PPR averages and configurable lineup slots.
- Data readiness endpoint with import timestamp and existing audit results.
- Local API smoke-tested for health, roster persistence, profiles, decision center, and data readiness.
- Server blocks HTTP access to private datasets, roster JSON, and source scripts; rejects cross-origin writes.
- Existing historical import, trade, backtesting and model tools retained.

## Important limitations
- **No guarantee of zero bugs.** 80 Python unit tests passed, JavaScript passed syntax validation, and local HTTP smoke tests passed. A full interactive browser test and live NFLverse download have **not** been verified.
- The Decision Center is **not** an injury-aware, schedule-aware or validated future projection. It uses historical PPR averages, even if you choose half-PPR or standard in league settings. It does not account for league scoring or positional replacement value yet. It intentionally says this in the UI.
- Roster settings support one league on one computer, with QB/RB/WR/TE/FLEX slots; K and DST can be stored but are not included in lineup scoring.
- This is a local single-user Python server, **not a production-hosted multi-user application**. Do not bind it to the public internet without authentication, rate limiting, separate data storage, and a production deployment review.
- NFLverse data authenticity, freshness and download availability require verification on your computer. No current injury, weather or live lineup feeds are connected.

## Test locally
`python -m unittest discover -s scripts -p 'test_*.py' -q`

## Branding
The website and local API are branded **FourthDown Analytics**. Verify trademark and domain availability before public launch.
# FourthDown Analytics Fantasy V15 — simplified navigation and importer fixes

## Quick start (Windows)
1. Install Python from https://www.python.org/downloads/ (check **Add Python to PATH**).
2. Extract this ZIP, open the project folder in File Explorer, enter `cmd` in the address bar.
3. Run `py server.py` (or `python server.py`).
4. Open http://127.0.0.1:8000 and select **Import**.
5. Choose a historical season range, or upload a compatible CSV.
6. Explore **Players**, **Matchups**, and **Accuracy**. Use **Fantasy tools** for advanced trade and start/sit analysis.

## GitHub
GitHub Desktop (optional): https://desktop.github.com/
GitHub account: https://github.com/signup
GitHub is not required for local imports. To run cloud workflows, publish this folder to a repository, enable Actions and grant workflow write permission as needed. No deployment or GitHub upload has been performed.

## Fixes
- Clearer four-tab navigation with keyboard focus styling and tab selection semantics.
- Player-name import accepts `player_display_name`, `player_name`, `player_name_full`, and `full_name`; it never substitutes fabricated names.
- Zero values for targets, carries and receptions display as zero instead of a missing-data dash.
- Player results update when season/position changes, with debounced name search.
- Input validation for historical season ranges.
- Removed wildcard cross-origin API header to reduce unintended access to the local API.

## Limitations
Player names, team IDs and statistics are imported as supplied by source; no authoritative identity reconciliation or live data validation has been performed. Historical downloads require internet access. Python tests do not prove the external data feed or browser integration works.

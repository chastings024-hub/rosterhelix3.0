# FourthDown Analytics Fantasy V21 — Native Trade and Start/Sit

This release replaces the embedded advanced-tools iframe on the main dashboard with native historical comparisons. Both tools use the same imported player-game history and show the recent PPR average, game sample size, and differences. The original `analytics.html` remains available for experimental tools.

## How to use
1. Extract the ZIP, stop the old server, open a terminal inside `fourthdown-analytics-v21`.
2. Run `py server.py` on Windows, then visit http://127.0.0.1:8000.
3. Import NFLverse historical data through Data Manager.
4. Open **Trade & Start/Sit**, choose a season and recent-game window, and load players.
5. For Start/Sit, enter two exact player names from the suggestion list. For trades, enter 1–3 player names per side, separated by commas.

## Important limitations
These are **historical PPR average comparisons**, not predictive Start/Sit or trade recommendations. The trade sum does not account for lineup slots, injuries, schedule, positional scarcity, or replacement players. Data quality depends on your import. Duplicate player names are rejected rather than silently matched to the wrong player. Live NFLverse syncing has not been verified in this environment.

## Validation
50 Python unit tests passed; JavaScript syntax passed Node `--check`. No full live-browser or live NFLverse sync test was performed.

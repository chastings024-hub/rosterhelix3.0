# FourthDown Analytics V23 — Walk-forward decision engine backtest

## What's new
Model Lab includes a second evaluation panel for the V22 decision engine. It compares matchup-adjusted estimates against the same model with a neutral opponent factor on identical player-games, using only earlier weeks within each season. It shows paired MAE, per-position MAE, sample size, and how often matchup adjustments were applied.

## Start
1. Extract the ZIP to a fresh folder.
2. Stop the old server (Ctrl+C), open a terminal in `fourthdown-analytics-v23`, run `py server.py`.
3. Open http://127.0.0.1:8000 and import historical statistics using Data Manager.
4. Open **Model Lab** → **Decision Engine Backtest**, choose season/window/history minimum, and click **Run backtest**.

## Methodology and caveats
The model uses prior player games and pooled historical opponent fantasy points allowed to a position. No future week is included in predictions. Only player-games with an opponent and enough prior player games are evaluated. The baseline uses the exact same recent/season shrinkage but no opponent adjustment. Positive MAE improvement means the adjusted model did better; negative means it did worse. The historical import source is not independently authenticated. This model is not calibrated and does not account for injuries, usage changes, schedule news or betting markets. Imported data is required; the package does not include verified NFL history.

## Verification
61 Python unit tests passed, Python compiled, and frontend JS passed Node syntax validation. Full browser integration and live NFLverse downloads were not verified.

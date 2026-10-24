# FourthDown Analytics Fantasy V22 — Experimental Decision Estimates

## New milestone
Adds an **Experimental Matchup-adjusted Estimates** panel within **Trade & Start/Sit**. It uses only the imported season's games before the chosen target week, computes season and recent PPR averages with small-sample shrinkage, reports observed targets/carries, and optionally applies a conservative defense-versus-position factor. Opponent effects require at least eight historical player-game samples and are capped at ±15%. The opponent entered is applied to all displayed players as a hypothetical comparison, not a verified schedule assignment.

## Install
Extract into a new folder, stop the old FourthDown Analytics server, open Command Prompt in `fourthdown-analytics-v22`, run `py server.py`, and visit http://127.0.0.1:8000. Import NFLverse data in Data Manager, then open Trade & Start/Sit. Select season, week, and optionally opponent, and click Calculate estimates.

## Limits
**These are experimental, uncalibrated estimates, not reliable predictions or trade recommendations.** No current injuries, depth charts, live role changes, verified upcoming schedules, or uncertainty calibration. Imported data is not independently verified. The earlier native Start/Sit and trade comparisons remain historical comparisons. The live NFLverse sync has not been tested end-to-end here.

## Validation
55 Python tests passed, Python compilation passed, JavaScript syntax passed with Node. Full browser integration and real-world forecast validation have not been performed.

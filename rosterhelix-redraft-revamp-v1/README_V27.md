# FourthDown Analytics Fantasy V27 — Three Milestones in One

## V25 — Out-of-sample validation
Select a model based on historical seasons ending in `Train through`, then evaluate it on later seasons. Selection is based on training MAE with a minimum of 20 eligible training player-games. Test data does not influence selection. Each week's estimates use earlier weeks within that season only.

## V26 — Position-level evaluation
The validation report breaks held-out errors down by QB, RB, WR, and TE and compares the selected strategy with a simple season-average baseline. Sample sizes are displayed, and small samples are flagged.

## V27 — Reports and safeguards
The Model Lab now includes a held-out validation panel and downloadable JSON report. Invalid or overlapping train/test year ranges are rejected. No strategy is deployed automatically, and results do not imply live predictive accuracy.

## Start
Extract this ZIP. In Windows File Explorer, open `fourthdown-analytics-v27`, click the address bar, type `cmd`, and run `py server.py`. Visit http://127.0.0.1:8000. Open Model Lab, import historical NFLverse data through Data Manager, then select earlier training and later test seasons.

## Limitations
Real-world NFLverse download and a full browser test have not been verified in this environment. Results require imported data, and data authenticity/completeness is not independently established. This is retrospective evaluation, not a live injury-aware prediction system. The position matchup adjustment is based on pooled player-games, not coverage assignments. Model variants are selected by training MAE only. The test split must be a later season and is not used for model selection. Missing data can bias results.

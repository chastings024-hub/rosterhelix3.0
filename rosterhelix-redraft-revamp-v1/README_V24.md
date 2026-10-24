# FourthDown Analytics Fantasy V24 — Model Optimization Lab

## What's new
Model Lab now offers six transparent historical prediction strategies: season average, 25%/50%/75% recent form, and 50% recent form with half/full matchup adjustment. All are scored on the same eligible player-games using earlier weeks of each season only. Results show sample size, MAE, and RMSE. The backend endpoint is `/api/model-optimization`.

## Run
Extract this ZIP, open Command Prompt in the `fourthdown-analytics-v24` folder, and run `py server.py`. Visit http://127.0.0.1:8000 and choose Model Lab → Model Optimization Lab. Historical data must be imported first.

## Limitations
The lowest-error variant is an exploratory winner **on the same data used to compare candidates**, not independently validated. V24 does not silently change live prediction weights. A future milestone should select on training seasons and evaluate once on held-out seasons. The historical opponent metric is based on position-level pooled player-game points, not a verified team coverage model. NFLverse live import has not been verified in this environment.

## Validation
66 Python unit tests pass. Python compilation passes. Full browser testing and live NFLverse download have not been performed.

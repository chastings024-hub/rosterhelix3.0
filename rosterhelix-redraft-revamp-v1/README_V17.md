# FourthDown Analytics V17 — Historical Data Quality Milestone

Adds **Data Manager → Audit imported data** and the `/api/history/audit` endpoint. Audits player-game counts, unique player IDs, distinct weeks, missing opponents and duplicate record keys per season. This helps determine whether imported data is complete enough for matchup modeling. It does not authenticate the upstream statistics.

## Start
Extract the archive, open a terminal in the `fourthdown-analytics-v17` directory, run `py server.py` (Windows) or `python server.py`, then open http://127.0.0.1:8000. Stop any older server first.

## Tests
Run `python -m unittest discover -s scripts -p 'test_*.py'`. Live NFLverse downloads and real-data model accuracy have not been independently verified in this environment. Import a historical CSV or use Data Manager's downloader, then run the audit.

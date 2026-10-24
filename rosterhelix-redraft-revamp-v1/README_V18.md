# FourthDown Analytics Fantasy V18 — Connection Diagnostics

## Start
Extract the archive. Open a terminal in the `fourthdown-analytics-v18` directory and run `py server.py` on Windows, or `python server.py` on other systems. Visit http://127.0.0.1:8000 and open **Data Manager**.

## Diagnose failed sync
Use **Check connection**, select 2024, and read the DNS / HTTP status and advice. This read-only test checks that the source is reachable and has a CSV-looking header. It does not prove the full file can be downloaded or validated. If the test passes, try downloading one season first. If it fails, use manual CSV upload and share the exact diagnostic result.

## Tests and limitations
46 Python tests pass; JavaScript syntax check passed. This environment has not verified an end-to-end live NFLverse download, browser rendering, or historical prediction accuracy. A successful connection check does not guarantee a full import. This release is focused on connection diagnostics, not changes to the prediction model.

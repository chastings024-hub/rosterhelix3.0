# FourthDown Analytics V16 — Interface redesign
The homepage now uses a two-column application layout with a persistent workspace sidebar on desktop and a compact horizontal navigation strip on mobile. The four main views are Player Explorer, Defense Matchups, Model Lab and Data Manager. Trade & Start/Sit links to analytics.html.

## Run
Extract the ZIP, open a terminal in the extracted folder, run `py server.py` on Windows (or `python server.py`), and visit http://127.0.0.1:8000 . Stop any older FourthDown Analytics server first, and hard-refresh the page with Ctrl+Shift+R.

## Testing
39 Python tests pass. The frontend JavaScript passed Node syntax validation. No end-to-end browser or live NFLverse sync verification was performed. V16 is a navigation/visual redesign; it does not fix an external data download failure.

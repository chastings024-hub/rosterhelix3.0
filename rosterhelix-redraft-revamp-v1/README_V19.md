# FourthDown Analytics Fantasy V19 — Brand-free theme upgrade

Two color schemes: Blue / White / Yellow (default) and Gold / Black / White (select from the top-right Theme menu). The theme is remembered in the browser when local storage is available. Both the dashboard and Advanced Analysis page honor the selected theme. No Chargers logos or NFL team branding.

## Changes
- New landing dashboard with quick navigation to existing functional tools.
- Real database readiness status, not fabricated stats.
- Redesigned navy sidebar, white cards, gold call-to-action buttons and mobile responsive navigation.
- Theme selector and matching styles for the advanced analytics page.
- Preserved V18.1 sync repair and historical import functionality.

## Start
1. Extract the ZIP.
2. Stop any older FourthDown Analytics server (`Ctrl+C`).
3. Open a terminal in `fourthdown-analytics-v19` and run `py server.py` (or `python server.py`).
4. Open http://127.0.0.1:8000 and refresh with Ctrl+Shift+R.
5. Choose a theme at the top right.

## Notes
The dashboard never invents statistics. Actual sync success and browser rendering depend on your environment.

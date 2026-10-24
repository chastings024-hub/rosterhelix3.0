# FourthDown Analytics Fantasy V20 — Unified workspace

V20 embeds the existing advanced fantasy analytics page within the main dashboard as a **Trade & Start/Sit** navigation section. The original advanced page remains accessible directly for compatibility. The iframe is same-origin and responds to theme changes.

## Run
Extract the ZIP; open the `fourthdown-analytics-v20` folder in Command Prompt; run `py server.py`; browse http://127.0.0.1:8000. Stop older server instances first.

## Notes
The advanced page is a legacy module embedded in the new shell, not yet a complete component-level rewrite. Legacy demo features still use fictional data when no actual data is loaded. Live NFLverse sync and browser-level integration have not been verified.

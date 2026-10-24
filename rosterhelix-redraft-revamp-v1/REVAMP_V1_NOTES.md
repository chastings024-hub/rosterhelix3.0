# RosterHelix redraft-first decision studio — incremental revamp

## Implemented
- More consolidated animated Decision Studio with three tabs: Start/Sit, Trade, Player Explorer.
- Opponent fields feed the existing shrunk/capped historical defensive adjustment, with sample disclosure.
- League-size selector (8–20) feeds the existing positional replacement model for trades.
- Searchable Player Explorer with median, observed quartiles, boom/bust and opportunity context.
- Trade output now includes largest single-player replacement surplus to expose quantity-for-quality pitfalls.
- Opportunity totals (targets + carries) added to player cards and comparisons.
- Responsive and reduced-motion friendly styling.

## Not yet implemented (must not be claimed)
- Live injuries, depth charts, snap share, routes, Vegas totals, confirmed next-week opponents, waiver availability, roster-aware trade acceptance, calibrated forecasts, real rest-of-season projections.
- Historical matchups require correctly imported opponent_team fields; no automatic current schedule lookup.
- Existing models are retrospective heuristics, not validated probabilities or trade market prices.

## Deployment
Back up your repository and persistent data first. Upload the files at the ZIP root to your repository root; Render redeploys on commit if auto-deploy is enabled. Do not overwrite your /var/data disk.

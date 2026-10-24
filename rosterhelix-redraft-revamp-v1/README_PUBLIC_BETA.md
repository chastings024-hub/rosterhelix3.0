# RosterHelix public beta

This package upgrades FourthDown Analytics V32 with the RosterHelix brand, account registration and sign-in, private per-user roster storage, administrator-only data importing, and a Render deployment blueprint with a persistent disk.

**Read `DEPLOY_RENDER.md` before deploying.** This is a small-scale public beta, not a fully audited production application. Accounts lack email verification, password reset, self-service deletion, and comprehensive abuse prevention. Do not invite a broad public audience until these gaps are addressed.

## Run locally

Python 3.11+ required. In this folder: `python server.py` (Windows: `py server.py`). Visit `http://127.0.0.1:8000/account.html`. The website is otherwise at `/`.

## Automated tests

`python -m unittest discover -s scripts -p "test_*.py" -q`

## Deploy

Push this folder to a **private GitHub repository** without `data/` files; in Render choose **New → Blueprint** and connect it. Blueprint provisions a paid web service and persistent disk. Configure `ADMIN_EMAIL` and keep the generated `ADMIN_API_KEY` secret. See `DEPLOY_RENDER.md` for Namecheap DNS records and verification.

## Data limitations

Historical datasets are not bundled or guaranteed current. The decision center uses historical data, not live injury/usage-aware predictions. Older README files document earlier versions and may refer to superseded local-only functionality.

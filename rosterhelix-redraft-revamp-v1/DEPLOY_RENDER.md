# RosterHelix — public beta deployment

**Status: small-scale public beta, not security-audited production software.** The app uses SQLite on a persistent Render disk. Accounts have email/password authentication, secure HttpOnly cookies on Render, CSRF headers for saved rosters, rate-limited login attempts, and user-specific roster data. There is no email verification, password reset, moderation, user data deletion UI, or comprehensive load/security testing. Do not market it as a fully hardened public service until these are added. Existing historical data imports are not independently verified or real-time.

## 1. GitHub

Create a **private GitHub repository**, e.g. `rosterhelix`, and upload this project's contents (not the parent directory). Keep all private data and passwords out of Git. GitHub's web upload works; a local Git client also works. Do not upload any `data/*.csv`, `data/*.json`, `data/*.sqlite3`, or `.env` files.

## 2. Render

Go to https://dashboard.render.com → **New → Blueprint**, connect the repository and approve the `render.yaml` setup. The Blueprint requests a **paid Starter web service and 1 GB persistent disk**. Check current Render pricing before approving. Set `ADMIN_EMAIL` to the exact email you'll register as your own account. Render also generates an `ADMIN_API_KEY` secret; retrieve it securely from the service environment only when you need to import/sync data. **Email alone does not grant import permissions.** Do not put your password in Render environment variables. Ensure the service and disk deploy successfully; check `https://YOUR-SERVICE.onrender.com/api/health`. Render automatically sets PORT. This is **one-instance hosting**; persistent disks cannot be shared by multiple instances.

**Do not use Render's free web service with this SQLite setup**: its filesystem is ephemeral and saved accounts/rosters would be lost. For larger scale, migrate accounts and rosters to PostgreSQL and add proper session management and migration tooling.

## 3. Test on Render's temporary URL

- Visit `https://YOUR-SERVICE.onrender.com/account.html`.
- Register your admin email and a strong unique password (12+ characters). Sign out, sign in, save a test roster and reload to confirm it persists.
- Create a separate test account and confirm its roster is private.
- Use the Data Manager as the administrator to import historical NFL game logs; regular accounts cannot sync/import. When prompted for the administrator import key, use `ADMIN_API_KEY` from Render.
- Redeploy and confirm both accounts and the imported data survive.

## 4. Namecheap custom domain

In Render → your web service → **Settings → Custom Domains**, add `rosterhelix.com` (or your exact purchased domain) and `www.rosterhelix.com`. Follow Render's verification instructions. At Namecheap → Domain List → Manage → Advanced DNS (assuming Namecheap BasicDNS), remove conflicting A/AAAA/CNAME/redirect records, **not unrelated MX/TXT records used for email**. Configure:

| Type | Host | Value |
|---|---|---|
| A | @ | 216.24.57.1 (verify Render's current displayed value) |
| CNAME | www | YOUR-SERVICE.onrender.com (use your actual Render hostname) |

Return to Render and click **Verify**. Wait for DNS propagation and TLS provisioning. Render handles HTTPS and redirects; test both apex and www addresses. If your Namecheap nameservers are pointed elsewhere, change DNS at that DNS provider instead.

## 5. Public-launch checklist

- Trademark clearance for RosterHelix; domain ownership is not trademark clearance.
- Add Terms of Service and Privacy Policy appropriate to your actual data practices; don't claim features you lack.
- Add email verification, password reset, abuse prevention, backups and restore drills, account deletion/export, monitoring, security review, and scalable PostgreSQL before wider launch.
- Do not upload real users' personal information to public GitHub or public logs.
- Test real NFLverse syncing and inspect data accuracy. Never label historical averages as guaranteed forecasts.

Sources: https://render.com/docs/configure-namecheap-dns , https://render.com/docs/disks , https://render.com/docs/custom-domains

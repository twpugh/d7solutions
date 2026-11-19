# Going live on Cloudflare Pages — D7's checklist

This takes d7solutions.net from its current host to D7's own Cloudflare account.
Everything up to step C6 is invisible to the public; the site keeps running on
the current host until the nameserver switch, and the current host stays
available as a fallback for a week after.

Two accounts are involved. **Every step below is done in D7's own Cloudflare
account** (signed in as admin@d7sol.com, the account named "Admin@d7sol.com's
Account" at the top left). If the account name at the top left shows anyone
else's account, stop and switch.

You need: a computer with Git and Node.js 20+ (for the `npx wrangler` commands;
everything except creating the database can also be done in the dashboard), a
Resend account (free), and someone from D7 present for the cutover call.

## B — build it in D7's account (nothing public changes)

- [ ] **B1 Pages project.** Dashboard › *Compute* › *Workers & Pages* › *Create*
      › *Pages* › *Connect to Git* › choose this repository.
      Production branch `main` · Framework preset **None** · Build command
      **(empty)** · Build output directory **`site`** · Save and Deploy.
      Expect: a `https://<project>.pages.dev` URL that shows the site. The
      contact form will answer "not set up yet" until B2.
- [ ] **B2 Leads database.** In a clone of this repo:
      ```bash
      npx wrangler login
      npx wrangler d1 create d7-leads
      ```
      Copy the `database_id` it prints into `wrangler.toml` (replace the zeros).
      Apply the table and push:
      ```bash
      npx wrangler d1 execute d7-leads --remote --file=schema.sql
      git commit -am "Bind leads database" && git push
      ```
      Expect: Pages redeploys; `https://<project>.pages.dev/api/health` shows
      `"contacts":0` instead of a warning.
      *(Dashboard alternative for the binding: Pages project › Settings › Bindings › Add › D1.)*
- [ ] **B3 Alerts (required).** Create a Resend account owned by D7. Add
      **`d7sol.com`** as a sending domain in Resend and add the DNS records it
      shows to wherever d7sol.com's DNS lives (Google Workspace's registrar or
      DNS host). Wait for Resend to show the domain *Verified*. Then:
      ```bash
      npx wrangler pages secret put RESEND_API_KEY      # paste the key when asked
      ```
      *(Dashboard: Pages › Settings › Variables and secrets › Add › type Secret.)*
      In `wrangler.toml`, set `ALERT_FROM` to an address on d7sol.com
      (e.g. `D7 Solutions website <website@d7sol.com>`) and check `ALERT_TO`.
      Commit and push.
- [ ] **B4 Backup proven.**
      ```bash
      npx wrangler d1 export d7-leads --remote --output=leads-test.sql
      ```
      Expect: a file. Keep doing this monthly (see README).
- [ ] **B5 End-to-end test on pages.dev.** Open
      `https://<project>.pages.dev/contact/`, submit a real message. Expect the
      page to say "we've got it" (not "saved, but…"), the email to arrive at the
      `ALERT_TO` addresses within a minute, and `/api/health` to show
      `"alerts":"email"` and `"pending_alerts":0`.
      **If the page says "saved, but our alert didn't go through": stop.**
      Alerts are not working; fix B3 before going further.
- [ ] **B6 Optional:** `npx wrangler pages secret put FLUSH_TOKEN` (any long
      random string). Then any scheduler can `POST
      https://www.d7solutions.net/api/alerts/flush` with header
      `X-Flush-Token: <that string>` to retry failed alerts.

## C — move the domain

- [ ] **C0 Preflight, day of cutover.** DNSSEC must be off:
      `curl -sH "accept: application/dns-json" "https://cloudflare-dns.com/dns-query?name=d7solutions.net&type=DS"`
      must show no `Answer`. (It was off on 2026-09-14.) Do **not** turn DNSSEC
      on in the new zone until a week after C6.
- [ ] **C1** Dashboard › *Domains* › *Add domain* › `d7solutions.net` › Free plan
      › **Manually enter DNS records** (not the automatic scan).
- [ ] **C2** Add exactly the two records in `dns-records.txt`. Nothing else.
- [ ] **C3** Write down the two nameservers Cloudflare assigns (Overview page).
      They look like `xxx.ns.cloudflare.com` / `yyy.ns.cloudflare.com`.
      _____________________________ / _____________________________
- [ ] **C4** Pages project › *Custom domains* › *Set up a custom domain* ›
      `www.d7solutions.net`, then again for `d7solutions.net`.
      Record what happened: ☐ both added and show *Pending*/*Verifying* (normal;
      they activate after C6) ☐ Cloudflare refused because the zone is not
      active yet → then do C4 immediately after C6, on the same call.
- [ ] **C5** Zone › *Rules* › *Redirect Rules* › create: when hostname equals
      `d7solutions.net` → dynamic redirect to
      `concat("https://www.d7solutions.net", http.request.uri.path)`, status 301.
- [ ] **C6 (Rob, on the call)** changes the domain's nameservers at the
      registrar to the pair from C3. From now on some visitors reach the new
      site and some the old for up to a day or two. That is expected.
- [ ] **C7 Watch.** Every 15 minutes for the first two hours, from a phone off
      Wi-Fi and from a laptop: `https://www.d7solutions.net/` loads with a valid
      certificate; `https://www.d7solutions.net/api/health` shows
      `"host":"cloudflare-pages"`; submit the contact form once and confirm the
      email. `dig +short NS d7solutions.net` should show the C3 pair.
- [ ] **C8 If anything fails** (site not found, certificate error, form error,
      no alert email): tell Rob; he puts the old nameservers back and the old
      host takes over again. Nothing on the old side is removed for a week.

## D — acceptance

- [ ] All of C7 green for 24 hours.
- [ ] `curl -sI http://d7solutions.net/lines/` returns `301` to `https://www.d7solutions.net/lines/`.
- [ ] `curl -sI https://www.d7solutions.net/portfolio` returns `301` to `/lines/`.
- [ ] Privacy notice at `/privacy/` reviewed and approved by D7 (it was
      rewritten for Cloudflare hosting on 2026-09-14).
- [ ] Ownership table completed:

| What | D7 account / person | Billing owner | Recovery (2FA, backup email) checked |
|---|---|---|---|
| Domain registration (GoDaddy, after Rob transfers it) | | | ☐ |
| Cloudflare account (zone, Pages, D1) | admin@d7sol.com | | ☐ |
| GitHub repository | | | ☐ |
| Resend (alert email) | | | ☐ |
| Who reads leads if alerts fail / checks `pending_alerts` | | n/a | n/a |
| Who runs the monthly D1 export | | n/a | n/a |
| Who edits content and runs the build | | n/a | n/a |
| Google Search Console (or "none") | | n/a | ☐ |

- [ ] D7 emails Rob: "d7solutions.net accepted on <date>". Rob then retires the
      old host a week after C6 and moves the domain registration to D7's
      GoDaddy account (you will get an email to accept it; accept within 10 days).

## After go-live

- Content changes: see README. Push to `main` = deployed.
- Monthly: `npx wrangler d1 export d7-leads --remote --output=leads-YYYYMMDD.sql`, keep the file somewhere safe.
- If `/api/health` ever shows `pending_alerts` above 0 for more than a day, read
  the leads directly (README) and check the Resend key.

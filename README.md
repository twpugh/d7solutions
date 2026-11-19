# d7solutions.net

> **Status (Nov 2026):** imported from the vendor hand-off package (prepared
> Cloudflare Pages release, source snapshot of 23 Oct 2026, every file checked
> against the hand-off SHA-256 manifest). Not yet deployed to Cloudflare; the
> live site is still served by the old host until cutover.
>
> **Preview:** every push to `main` publishes `site/` to GitHub Pages via
> `.github/workflows/preview-pages.yml`. The contact form does not work on the
> preview (GitHub Pages can't run `functions/`).
>
> **Never commit secrets or lead data.** API keys and tokens go in Cloudflare
> Pages › Settings › Variables and secrets.

The D7 Solutions website: a static site plus a contact form, hosted on
**Cloudflare Pages** with the form's leads in a **Cloudflare D1** database.
No server to run.

```
visitor -> Cloudflare (TLS, edge) -> Pages static files + functions/api/*
                                          |
                                          +-> D1 "d7-leads"  (every submission, stored first)
                                          +-> alert email (Resend) or webhook, retried if it fails
```

First-time setup and the go-live steps are in [`CUTOVER.md`](CUTOVER.md).

## Layout

```
build/content.py   ALL site copy, lines, territory   <- edit this, not templates
build/build.py     generator: content + templates -> site/
templates/         Jinja2 templates
content/posts/     blog posts as markdown (front matter + body)
content/pages/     prose pages (privacy notice)
assets/            css, logos, images (copied verbatim)
pages/             _headers and _redirects, copied to site/ by the build
site/              GENERATED - never edit by hand; build.py wipes it. Committed, so Pages needs no build step.
functions/api/     contact.js (form intake), health.js, alerts/flush.js
schema.sql         the D1 table
wrangler.toml      Pages project config: output dir, D1 binding, non-secret alert settings
```

## Everyday tasks

**Change wording, a line, a rep, or territory** → edit `build/content.py`, then

```bash
python build/build.py
git add -A && git commit -m "Update copy" && git push
```

Pages deploys `main` on every push (about a minute). Needs Python 3 with
`pip install markdown jinja2`.

**Add a blog post** → drop a markdown file in `content/posts/`:

```markdown
---
title: Your Title
author: D7 Solutions
date: Sep 4
read_time: 4 min read
slug: your-url-slug
---

Body in markdown. First paragraph becomes the excerpt.
```

Rebuild, commit, push. It appears on `/blog/` and at `/post/your-url-slug`.

**Territory is derived, never asserted.** The footer, the map and the "N
states" copy are computed from the `states` lists in `content.py`. Adding a
state to a line is the only way to make the site claim it.

## Contact form and lead alerts

`POST /api/contact` → validates → row in D1 → alert. Every submission is stored
**before** any alert is attempted, so a delivery failure can lose an alert but
never a lead. The response says `"stored"` instead of `"sent"` whenever no
alert went out, and the page then tells the visitor to call instead of promising
a quick reply.

Settings (Pages › Settings › Variables and secrets, or `wrangler.toml` for the non-secret ones):

| Name | Secret? | Meaning |
|---|---|---|
| `RESEND_API_KEY` | yes | Resend API key. With `ALERT_TO`, enables email alerts. |
| `ALERT_TO` | no | Comma-separated recipients (in `wrangler.toml`). |
| `ALERT_FROM` | no | Sender, must be on a domain verified in Resend (in `wrangler.toml`). |
| `ALERT_WEBHOOK` | no | Fallback: POST JSON to this URL when no Resend key is set. |
| `FLUSH_TOKEN` | yes | Optional. Enables `POST /api/alerts/flush` (header `X-Flush-Token`) to retry failed alerts on demand. |

Failed alerts are recorded on the lead (`alert_attempts`, `last_alert_error`)
and retried automatically after the next successful delivery, or via the flush
endpoint. `GET /api/health` shows `pending_alerts`; if it is ever non-zero for
long, the alert channel is broken and someone must read the leads directly.

**Read leads:**

```bash
npx wrangler d1 execute d7-leads --remote --command "select id,created_utc,name,email,company,topic,notified from contact order by id desc limit 20"
```
or Dashboard › Storage & databases › D1 › d7-leads › Console.

**Back up leads** (do this monthly, and before any schema change):

```bash
npx wrangler d1 export d7-leads --remote --output=leads-$(date +%Y%m%d).sql
```

**Delete a lead** on request: `... --command "DELETE FROM contact WHERE id=<n>"`.

Protections: honeypot field, 5 submissions per IP per 10 minutes (soft), 64 KB
body cap, per-field length caps, email shape check.

## Health

`https://www.d7solutions.net/api/health` → `{"ok":true, "pages":10, "built":"…",
"contacts":N, "pending_alerts":0, "alerts":"email", …}`. `pending_alerts` should be 0.

## Local preview

```bash
npm install -g wrangler        # once (Node 20+)
npx wrangler d1 execute d7-leads --local --file=schema.sql
npx wrangler pages dev         # prints the local URL to open
```

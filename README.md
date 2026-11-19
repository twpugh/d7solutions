# d7solutions.net

Source for the D7 Solutions public website, https://www.d7solutions.net/.

## Plan

The site is a static site (HTML, CSS, browser JavaScript, an SVG territory map) with a
small contact-form backend. It is moving from a vendor-operated server into D7-owned
accounts:

- **Source and history:** this repository.
- **Hosting:** Cloudflare Pages, deployed from this repository and fronted by Cloudflare
  for `d7solutions.net` / `www.d7solutions.net`.
- **Contact form:** Pages Functions with durable lead storage (Cloudflare D1) and email
  alerts. Not yet set up.

The current public site stays in service until a private preview has been built and
accepted.

## Secrets

Never commit passwords, API keys, app passwords, tunnel credentials, webhook URLs or
lead data. Configure them as Cloudflare Pages environment variables or secrets.

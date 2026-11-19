/**
 * GET /api/health
 *
 * Reports whether the leads database is bound, how many leads exist, how many
 * still have no delivered alert, and the last alert error. It does NOT list
 * recipient addresses (a public endpoint has no reason to). "pages" and
 * "built" come from site/build.json, which build.py writes, so the count
 * cannot drift from the content.
 */
import { configured, recipients } from "./contact.js";

const headers = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" };

export async function onRequestGet({ request, env }) {
  const body = { ok: true, site: "d7solutions.net", host: "cloudflare-pages" };
  try {
    try {
      const r = await env.ASSETS.fetch(new URL("/build.json", request.url));
      if (r.ok) Object.assign(body, await r.json());
    } catch { /* build.json is informational only */ }

    if (env.LEADS) {
      const t = await env.LEADS.prepare(
        "SELECT COUNT(*) AS n, SUM(notified=0) AS pending FROM contact").first();
      body.contacts = t.n;
      body.pending_alerts = t.pending || 0;
      if (body.pending_alerts) {
        const e = await env.LEADS.prepare(
          "SELECT last_alert_attempt_utc, last_alert_error FROM contact WHERE notified=0 " +
          "ORDER BY id DESC LIMIT 1").first();
        body.last_alert_attempt_utc = e?.last_alert_attempt_utc || null;
        body.last_alert_error = e?.last_alert_error || null;
      }
    } else {
      body.contacts = null;
      body.pending_alerts = null;
      body.warning = "no LEADS database bound - the contact form returns 503";
    }
    body.alerts = configured(env) || "not configured";
    body.alert_recipients = recipients(env).length;   // a count, never the addresses
    return new Response(JSON.stringify(body), { headers });
  } catch (e) {  // health must report failure, not become one
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers });
  }
}

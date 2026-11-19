/**
 * POST /api/contact — contact-form intake for d7solutions.net on Cloudflare Pages.
 *
 * Contract the page's JavaScript (templates/contact.html) speaks:
 *
 *   request  JSON {name, email, company, phone, topic, project, message, website}
 *   200      {ok:true, id, status:"sent"|"stored"}
 *   400/413/429/503  {error:"human-readable text"}
 *
 * Every submission is stored in D1 (binding LEADS) BEFORE any alert is tried,
 * so a delivery failure can lose an alert but never a lead. The response says
 * "stored", not "sent", whenever no alert channel delivered — it never claims
 * an email went out. The page shows a different message for "stored".
 *
 * Alert channels, tried in this order (set as Pages variables / secrets):
 *   RESEND_API_KEY + ALERT_TO (+ ALERT_FROM)  -> email via https://resend.com
 *   ALERT_WEBHOOK                             -> POST JSON to any catch hook
 * ALERT_TO is comma-separated. ALERT_FROM must be on a domain verified in Resend.
 *
 * Alert recovery: every attempt is recorded on the row (alert_attempts, last_alert_attempt_utc,
 * last_alert_error). After any successful delivery, older rows still at
 * notified=0 are retried in the background. POST /api/alerts/flush retries
 * them on demand. /api/health shows how many are pending.
 *
 * Rate limit: 5 submissions per IP per 10 minutes, counted in D1. It is a soft
 * abuse control — concurrent requests at the edge can each read the count
 * before the others insert — not a strict guarantee. Cloudflare's own rate
 * limiting rules are the strict layer if one is ever needed.
 */

const FIELDS = ["name", "email", "company", "phone", "topic", "project", "message"];
const LIMITS = { name: 120, email: 200, company: 160, phone: 40,
                 topic: 40, project: 200, message: 8000 };
const MAX_BODY = 64 * 1024;
const RATE_LIMIT = 5;          // submissions ...
const RATE_WINDOW_S = 600;     // ... per IP per 10 minutes
const EMAIL_RE = /^[^@\s]+@[^@\s.]+\.[^@\s]+$/;
const PHONE_FALLBACK = "402.709.3150";
const FLUSH_LIMIT = 20;

const TOPICS = {
  "general": "General inquiry",
  "lunch-and-learn": "Lunch & learn request",
  "product-data": "Product data / submittals",
  "assembly": "Assembly or detail question",
  "pricing": "Budget pricing",
  "rep-inquiry": "Manufacturer / rep inquiry",
};

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });

const utc = (d = new Date()) => d.toISOString().replace(/\.\d{3}Z$/, "+00:00");

function log(event, fields = {}) {
  console.log(JSON.stringify({ ts: new Date().toISOString(), event, ...fields }));
}

// ---------------------------------------------------------------------------
// alerts
// ---------------------------------------------------------------------------
export function recipients(env) {
  return String(env.ALERT_TO || "").split(",").map(s => s.trim()).filter(Boolean);
}

export function configured(env) {
  if (env.RESEND_API_KEY && recipients(env).length) return "email";
  if (env.ALERT_WEBHOOK) return "webhook";
  return null;
}

/** A display name safe to put in an address header: no line breaks, brackets or quotes. */
function headerName(s) {
  return String(s || "").replace(/[\r\n\t<>"\\]/g, " ").replace(/\s+/g, " ").trim().slice(0, 80);
}

function emailBody(lead, id) {
  const lines = [
    ["Name", lead.name], ["Email", lead.email], ["Company", lead.company],
    ["Phone", lead.phone], ["Project", lead.project],
    ["Topic", TOPICS[lead.topic] || lead.topic || "General inquiry"],
  ].filter(([, v]) => v);
  const out = ["A new enquiry came in through d7solutions.net.", ""];
  for (const [k, v] of lines) out.push(`${(k + ":").padEnd(9)} ${v}`);
  out.push("", "Message:", "", (lead.message || "").trim(), "");
  if (id) out.push(`(reference #${id})`);
  return out.join("\n");
}

async function sendEmail(env, lead, id) {
  const topic = TOPICS[lead.topic] || "New enquiry";
  const who = headerName(lead.name) || "Someone";
  const subject = `D7 lead: ${topic} - ${who}` + (lead.company ? ` (${headerName(lead.company)})` : "");
  const from = env.ALERT_FROM || "D7 Solutions website <website@d7solutions.net>";
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`,
               "Content-Type": "application/json" },
    body: JSON.stringify({
      from, to: recipients(env), subject, text: emailBody(lead, id),
      // So a reply goes straight to the enquirer, not back to the website.
      ...(lead.email ? { reply_to: `${who} <${lead.email}>` } : {}),
    }),
  });
  if (!res.ok) throw new Error(`resend ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return "email";
}

async function sendWebhook(env, lead, id) {
  const res = await fetch(env.ALERT_WEBHOOK, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...lead, id, site: "d7solutions.net",
                           subject: `D7 lead: ${lead.name || "enquiry"}` }),
  });
  if (!res.ok) throw new Error(`webhook ${res.status}`);
  return "webhook";
}

/**
 * Deliver one alert and record the attempt on the row. Never throws — the lead
 * is already stored. Returns true only when a channel actually delivered.
 */
export async function alertRow(env, row) {
  const lead = {};
  for (const f of FIELDS) lead[f] = row[f] ?? "";
  const id = row.id;
  const path = configured(env);
  let sent = false, err = null;
  if (!path) {
    log("alert_dry_run", { id });
    err = "no alert channel configured";
  } else {
    try {
      const via = path === "email" ? await sendEmail(env, lead, id) : await sendWebhook(env, lead, id);
      log("alert_sent", { id, via });
      sent = true;
    } catch (e) {
      // Loudly: a silent alert failure is how leads go cold.
      err = `${path}: ${String(e).slice(0, 300)}`;
      log("alert_failed", { id, via: path, err });
    }
  }
  await env.LEADS.prepare(
    "UPDATE contact SET notified=?1, alert_attempts=alert_attempts+1, " +
    "last_alert_attempt_utc=?2, last_alert_error=?3 WHERE id=?4")
    .bind(sent ? 1 : 0, utc(), err, id).run();
  return sent;
}

/** Retry alerts for stored leads that were never delivered. Oldest first. */
export async function flushPending(env, { limit = FLUSH_LIMIT, except = null } = {}) {
  if (!env.LEADS || !configured(env)) return { pending: 0, sent: 0 };
  const { results } = await env.LEADS.prepare(
    "SELECT * FROM contact WHERE notified=0 AND (?1 IS NULL OR id<>?1) ORDER BY id LIMIT ?2")
    .bind(except, limit).all();
  let sent = 0;
  for (const row of results) if (await alertRow(env, row)) sent += 1;
  if (results.length) log("alerts_flushed", { pending: results.length, sent });
  return { pending: results.length, sent };
}

// ---------------------------------------------------------------------------
// request
// ---------------------------------------------------------------------------
export async function onRequestPost({ request, env, waitUntil }) {
  const ip = request.headers.get("cf-connecting-ip") || "?";

  const raw = await request.arrayBuffer();
  if (raw.byteLength > MAX_BODY) return json({ error: "Message too large." }, 413);
  let data;
  try {
    data = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw));
    if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("not an object");
  } catch {
    return json({ error: "Could not read that submission." }, 400);
  }

  // Honeypot: a filled hidden field means a bot. Answer 200 so it doesn't retry.
  if (String(data.website ?? "").trim()) { log("contact_honeypot", { ip }); return json({ ok: true }); }

  const clean = {};
  for (const f of FIELDS) {
    const v = data[f] == null ? "" : String(data[f]).replace(/\x00/g, "").trim();
    clean[f] = v.slice(0, LIMITS[f]);
  }
  if (!clean.name || !clean.email || !clean.message)
    return json({ error: "Please fill in your name, email, and a message." }, 400);
  if (!EMAIL_RE.test(clean.email))
    return json({ error: "That email address doesn't look right." }, 400);

  if (!env.LEADS) {
    // No database bound: refuse rather than pretend. The visitor gets a phone number.
    log("contact_unconfigured", { ip });
    return json({ error: `The contact form is not set up yet. Please call us at ${PHONE_FALLBACK}.` }, 503);
  }

  const since = utc(new Date(Date.now() - RATE_WINDOW_S * 1000));
  const { n } = await env.LEADS.prepare(
    "SELECT COUNT(*) AS n FROM contact WHERE ip = ?1 AND created_utc >= ?2").bind(ip, since).first();
  if (n >= RATE_LIMIT)
    return json({ error: `Too many messages from this connection. Please call us at ${PHONE_FALLBACK}.` }, 429);

  const ins = await env.LEADS.prepare(
    "INSERT INTO contact(created_utc,name,email,company,phone,topic,project,message,ip,user_agent) " +
    "VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)")
    .bind(utc(), clean.name, clean.email, clean.company, clean.phone, clean.topic,
          clean.project, clean.message, ip, (request.headers.get("user-agent") || "").slice(0, 300))
    .run();
  const id = ins.meta.last_row_id;

  const sent = await alertRow(env, { id, ...clean });
  if (sent && typeof waitUntil === "function") {
    // Delivery works right now: catch up on anything that failed earlier,
    // without holding the visitor's response for it.
    waitUntil(flushPending(env, { except: id }).catch(e => log("alert_flush_failed", { err: String(e) })));
  }
  log("contact_received", { id, topic: clean.topic, notified: sent });
  return json({ ok: true, id, status: sent ? "sent" : "stored" });
}

export const onRequestGet = () => json({ error: "Method not allowed" }, 405);

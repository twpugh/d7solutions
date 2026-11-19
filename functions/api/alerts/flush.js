/**
 * POST /api/alerts/flush — retry alerts for stored leads that were never delivered.
 *
 * Guarded by a shared secret so only D7 can trigger it:
 *   npx wrangler pages secret put FLUSH_TOKEN      (any long random string)
 *   curl -X POST -H "X-Flush-Token: <token>" https://www.d7solutions.net/api/alerts/flush
 *
 * With no FLUSH_TOKEN configured the route answers 404, so it is inert until
 * D7 chooses to use it. Point any external scheduler (a cron service, or a
 * Cloudflare Worker cron trigger) at it to get periodic retries.
 */
import { flushPending, configured } from "../contact.js";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });

export async function onRequestPost({ request, env }) {
  const token = env.FLUSH_TOKEN;
  if (!token) return json({ error: "Not found" }, 404);
  if ((request.headers.get("x-flush-token") || "") !== token) return json({ error: "Forbidden" }, 403);
  if (!env.LEADS) return json({ error: "no LEADS database bound" }, 503);
  const res = await flushPending(env, { limit: 50 });
  return json({ ok: true, ...res, alerts: configured(env) || "not configured" });
}

export const onRequestGet = () => json({ error: "Method not allowed" }, 405);

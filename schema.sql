-- D1 schema for the d7solutions.net contact form (binding LEADS).
-- One row per submission, plus alert-attempt state so a failed alert is
-- visible and retryable instead of silently stuck at notified=0.
--
--   wrangler d1 create d7-leads                       (once; paste the id into wrangler.toml)
--   wrangler d1 execute d7-leads --remote --file=schema.sql
--   wrangler d1 execute d7-leads --local  --file=schema.sql   (for `wrangler pages dev`)
--
-- Export (backup):  wrangler d1 export d7-leads --remote --output=leads-YYYYMMDD.sql
-- Restore:          wrangler d1 execute d7-leads --remote --file=leads-YYYYMMDD.sql
-- Delete one lead:  wrangler d1 execute d7-leads --remote --command "DELETE FROM contact WHERE id=<n>"

CREATE TABLE IF NOT EXISTS contact(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_utc TEXT NOT NULL,
    name TEXT, email TEXT, company TEXT, phone TEXT,
    topic TEXT, project TEXT, message TEXT,
    ip TEXT, user_agent TEXT,
    notified INTEGER NOT NULL DEFAULT 0,
    alert_attempts INTEGER NOT NULL DEFAULT 0,
    last_alert_attempt_utc TEXT,
    last_alert_error TEXT
);
CREATE INDEX IF NOT EXISTS ix_contact_created ON contact(created_utc);
CREATE INDEX IF NOT EXISTS ix_contact_ip_created ON contact(ip, created_utc);
CREATE INDEX IF NOT EXISTS ix_contact_pending ON contact(notified, id);

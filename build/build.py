# -*- coding: utf-8 -*-
"""Static site generator for d7solutions.net.

Reads content/ + templates/ and writes site/. Deterministic and idempotent:
running it twice produces byte-identical output, so a rebuild during a live
request never yields a half-written page (files are written atomically).

Usage:  python build/build.py
"""
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
TPL = os.path.join(ROOT, "templates")
OUT = os.path.join(ROOT, "site")
ASSETS = os.path.join(ROOT, "assets")
POSTS = os.path.join(ROOT, "content", "posts")
PAGES = os.path.join(ROOT, "content", "pages")

MD = markdown.Markdown(extensions=["extra", "sane_lists"])


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def write(rel_path, text):
    """Write a page, creating parent dirs. Paths are site-relative."""
    path = os.path.join(OUT, rel_path.lstrip("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)
    return path


def read_front_matter(path):
    """Parse a `---` front-matter block plus markdown body."""
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        return {}, raw
    meta = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()


def excerpt_of(md_body, limit=165):
    """First real sentence(s) of a post, as plain text."""
    for para in md_body.split("\n\n"):
        p = para.strip()
        if not p or p.startswith(("#", "-", "!", ">")):
            continue
        p = re.sub(r"\*\*|\*|`", "", p)
        p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) <= limit:
            return p
        cut = p[:limit].rsplit(" ", 1)[0]
        return cut.rstrip(".,;:") + "..."
    return C.SITE["description"]


def sort_key(meta):
    """Posts carry Wix's display date ('Apr 1'); keep a stable order."""
    months = ("jan feb mar apr may jun jul aug sep oct nov dec").split()
    d = (meta.get("date") or "").strip().lower()
    m = re.match(r"([a-z]{3})[a-z]*\s+(\d+)", d)
    if m and m.group(1) in months:
        return (months.index(m.group(1)) + 1, int(m.group(2)))
    return (99, 99)


# --------------------------------------------------------------------------
# territory map
# --------------------------------------------------------------------------
def map_context():
    """Build the SVG paths/labels and the JSON the map script reads."""
    P = json.load(open(os.path.join(BUILD, "paths.json"), encoding="utf-8"))
    states = P["states"]
    paths, labels = [], []
    for ab in C.STATE_ORDER:
        s = states[ab]
        paths.append(
            f'<path id="st-{ab}" class="state" data-ab="{ab}" '
            f'd="{s["d"]}" tabindex="0" role="button" '
            f'aria-label="{C.STATE_NAMES[ab]}"></path>'
        )
        labels.append(f'<text class="lbl" id="lbl-{ab}" x="{s["cx"]}" y="{s["cy"]}">{ab}</text>')

    data = [
        {
            "name": l["name"],
            "lane": l["lane"],
            "logo": l["logo"],
            "color": l["color"],
            "states": l["states"],
            "territory_note": l.get("territory_note", ""),
        }
        for l in C.LINES
    ]
    # paths.json stores viewBox as [width, height]. It must be rendered as the
    # 4-value SVG form — a bare "[760, 810.2]" is invalid, and the browser
    # silently discards it and draws the map unscaled (i.e. cropped to the
    # top-left corner) rather than erroring.
    # Crop the viewBox to the states actually drawn, so dropping a state from
    # STATE_ORDER doesn't leave an empty band where it used to be. Paths are
    # absolute M/L commands, so every number pair is a point.
    xs, ys = [], []
    for ab in C.STATE_ORDER:
        nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", states[ab]["d"])]
        xs += nums[0::2]
        ys += nums[1::2]
    pad = 8
    x0, y0 = min(xs) - pad, min(ys) - pad
    viewbox = f"{x0:.1f} {y0:.1f} {max(xs) - x0 + pad:.1f} {max(ys) - y0 + pad:.1f}"

    return {
        "map_viewbox": viewbox,
        "map_paths": "\n      ".join(paths),
        "map_labels": "\n      ".join(labels),
        "map_data": data,
        # Rendered raw into a <script> block, so neutralise any "</script>"
        # a future line name or note could introduce.
        "map_json": json.dumps(
            {"lines": data, "names": C.STATE_NAMES}, separators=(",", ":")
        ).replace("<", "\\u003c"),
    }


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    # assets are copied verbatim; site.css is hashed for cache-busting
    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))
    css = open(os.path.join(ASSETS, "site.css"), "rb").read()
    cachebust = hashlib.sha256(css).hexdigest()[:10]

    env = Environment(
        loader=FileSystemLoader(TPL),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["state_name"] = lambda ab: C.STATE_NAMES.get(ab, ab)

    org_jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": C.SITE["name"],
        "url": C.SITE["base_url"],
        "description": C.SITE["description"],
        "areaServed": [C.STATE_NAMES[a] for a in C.STATE_ORDER],
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "name": c["name"], "contactType": c["title"],
                "telephone": c["phone_href"], "email": c["email"],
            } for c in C.CONTACTS
        ],
    }, separators=(",", ":"))

    # Derived, never hand-written: the states we actually represent a line in.
    # The June build hard-coded "8 states" while the line data covered 6, and
    # the two drifted apart silently. Anything the site *claims* about coverage
    # is computed from LINES so it cannot say more than the data supports.
    covered = [ab for ab in C.STATE_ORDER
               if any(ab in l["states"] for l in C.LINES)]
    regional = [ab for ab in C.STATE_ORDER if ab not in covered]

    # Same reason: the headline count is computed, never typed. Removing a line
    # from content.py must not leave the site still saying "six manufacturers".
    _WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
              6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}
    line_count_word = _WORDS.get(len(C.LINES), str(len(C.LINES)))

    base = {
        "site": C.SITE,
        "nav": C.NAV,
        "covered": covered,
        "covered_names": [C.STATE_NAMES[a] for a in covered],
        "regional_names": [C.STATE_NAMES[a] for a in regional],
        "line_count": len(C.LINES),
        "line_count_word": line_count_word,
        "contacts": C.CONTACTS,
        "lines": C.LINES,
        "systems": C.SYSTEMS,
        "markets": C.MARKETS,
        # Table columns: most lines covered first; ties keep STATE_ORDER.
        "state_order": sorted(
            C.STATE_ORDER,
            key=lambda ab: -sum(ab in l["states"] for l in C.LINES),
        ),
        "year": date.today().year,
        "cachebust": cachebust,
        "jsonld": org_jsonld,
    }
    mapctx = map_context()

    urls = []

    def render(tpl, rel, url, **extra):
        html = env.get_template(tpl).render(page_url=url, **base, **extra)
        write(rel, html)
        urls.append(url)

    # ---- posts -----------------------------------------------------------
    posts = []
    if os.path.isdir(POSTS):
        for fn in sorted(os.listdir(POSTS)):
            if not fn.endswith(".md"):
                continue
            meta, body = read_front_matter(os.path.join(POSTS, fn))
            slug = meta.get("slug") or fn[:-3]
            MD.reset()
            posts.append({
                "slug": slug,
                "url": f"/post/{slug}",
                "title": meta.get("title", slug),
                "author": meta.get("author", "D7 Solutions"),
                "date_display": meta.get("date", ""),
                "read_time": meta.get("read_time", ""),
                "excerpt": excerpt_of(body),
                "body": MD.convert(body),
                "_sort": sort_key(meta),
            })
    posts.sort(key=lambda p: p["_sort"])

    for p in posts:
        others = [q for q in posts if q["slug"] != p["slug"]][:3]
        # post/<slug>.html, not post/<slug>/index.html: the canonical URL is
        # /post/<slug> (no trailing slash) and Cloudflare Pages serves a bare
        # .html at exactly that path, redirecting the slashed form back to it.
        render("post.html", f"post/{p['slug']}.html", p["url"],
               post=p, other_posts=others)

    # ---- core pages ------------------------------------------------------
    render("home.html", "index.html", "/", **mapctx)
    render("lines.html", "lines/index.html", "/lines/")
    render("territory.html", "territory/index.html", "/territory/", **mapctx)
    render("blog.html", "blog/index.html", "/blog/", posts=posts)
    render("contact.html", "contact/index.html", "/contact/")

    # ---- prose pages -----------------------------------------------------
    if os.path.isdir(PAGES):
        for fn in sorted(os.listdir(PAGES)):
            if not fn.endswith(".md"):
                continue
            meta, body = read_front_matter(os.path.join(PAGES, fn))
            slug = meta.get("slug") or fn[:-3]
            MD.reset()
            page = {
                "title": meta.get("title", slug),
                "subtitle": meta.get("subtitle", ""),
                "description": meta.get("description", C.SITE["description"]),
                "body": MD.convert(body)
                + (f'\n<p style="margin-top:32px;color:var(--muted);font-size:.88rem">'
                   f'Last updated {meta["updated"]}.</p>' if meta.get("updated") else ""),
            }
            render("prose.html", f"{slug}/index.html", f"/{slug}/", page=page)

    # ---- 404 (served by the app, not linked) -----------------------------
    html = env.get_template("404.html").render(page_url="/404", **base)
    write("404.html", html)

    # ---- sitemap + robots ------------------------------------------------
    today = date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{C.SITE['base_url']}{u}</loc>"
                  f"<lastmod>{today}</lastmod></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")

    write("robots.txt",
          "User-agent: *\nAllow: /\n\n"
          f"Sitemap: {C.SITE['base_url']}/sitemap.xml\n")

    # favicon: a D7 monogram, drawn rather than shipped as a binary
    write("assets/favicon.svg",
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
          '<rect width="64" height="64" rx="12" fill="#0f1620"/>'
          '<text x="32" y="44" font-family="Georgia,serif" font-size="34" '
          'font-weight="600" text-anchor="middle" fill="#ffffff">D'
          '<tspan fill="#0B5FA5">7</tspan></text></svg>\n')

    # Build stamp read by /api/health, so the page count it reports is the real
    # one (urls + the 404 page) rather than a constant that drifts.
    write("build.json", json.dumps({"pages": len(urls) + 1, "built": today},
                                   separators=(",", ":")) + "\n")
    # Cloudflare Pages control files (_headers, _redirects) live in pages/ and
    # are copied to the site root, because this function wipes site/ first.
    pages_dir = os.path.join(ROOT, "pages")
    if os.path.isdir(pages_dir):
        for fn in sorted(os.listdir(pages_dir)):
            if fn.startswith("_"):
                shutil.copyfile(os.path.join(pages_dir, fn), os.path.join(OUT, fn))
    print(f"built {len(urls)} pages -> {OUT}")
    for u in urls:
        print("  ", u)
    return 0


if __name__ == "__main__":
    sys.exit(main())

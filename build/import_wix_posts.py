# -*- coding: utf-8 -*-
"""One-time importer: Wix blog post HTML -> markdown in content/posts/.

Run once to migrate off Wix. After that the markdown files in content/posts/
are the source of truth and this script is only kept for provenance.

Usage:  python build/import_wix_posts.py <raw-html-dir>
"""
import html
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(DIR), "content", "posts")


def to_markdown(seg: str) -> str:
    """Convert the Wix article body to markdown.

    Deliberately narrow: Wix emits h2/h3/p/ul/li and nothing else here, so a
    real HTML parser would be more machinery than the job needs.
    """
    # Drop everything before the body content (title/author/date are metadata,
    # captured separately) and everything after it (share bar, comments).
    seg = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", seg, flags=re.S)
    seg = re.sub(r"<figure.*?</figure>", "", seg, flags=re.S)

    # Inline formatting first, while tags still delimit it.
    seg = re.sub(r"<(strong|b)\b[^>]*>(.*?)</\1>", r"**\2**", seg, flags=re.S)
    seg = re.sub(r"<(em|i)\b[^>]*>(.*?)</\1>", r"*\2*", seg, flags=re.S)
    seg = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", seg, flags=re.S)

    # Block structure -> markdown markers.
    for n, mark in ((2, "## "), (3, "### "), (4, "#### ")):
        seg = re.sub(rf"<h{n}\b[^>]*>(.*?)</h{n}>", rf"\n\n{mark}\1\n\n", seg, flags=re.S)
    # Wix nests <p> (and wrapper <div>s) *inside* <li>, so the generic <p> rule
    # below would split one bullet across three lines. Flatten the li first.
    def _li(m):
        inner = re.sub(r"</?(p|div|span)\b[^>]*>", " ", m.group(1), flags=re.S)
        inner = re.sub(r"\s+", " ", inner).strip()
        return f"\n- {inner}"

    seg = re.sub(r"<li\b[^>]*>(.*?)</li>", _li, seg, flags=re.S)
    seg = re.sub(r"<p\b[^>]*>(.*?)</p>", r"\n\n\1\n\n", seg, flags=re.S)
    seg = re.sub(r"<br\s*/?>", "\n", seg)

    # Strip whatever tags remain, then normalise whitespace.
    seg = re.sub(r"<[^>]+>", "", seg)
    seg = html.unescape(seg)
    seg = seg.replace(" ", " ")
    seg = re.sub(r"[ \t]+", " ", seg)
    seg = re.sub(r" *\n *", "\n", seg)
    seg = re.sub(r"\n{3,}", "\n\n", seg)

    # Unwrapping inner <span>/<p> leaves gaps inside the emphasis markers
    # ("** Insulation ** :"), which markdown will not render as bold at all.
    seg = re.sub(r"\*\*\s*(.+?)\s*\*\*", r"**\1**", seg)
    seg = re.sub(r"(?<!\*)\*\s*([^*\n]+?)\s*\*(?!\*)", r"*\1*", seg)
    seg = re.sub(r"\*\*\s+([:.,;!?])", r"**\1", seg)

    # A heading immediately followed by its own duplicate line happens when Wix
    # wraps a heading in a <p> as well; collapse it.
    lines, cleaned = seg.strip().split("\n"), []
    for ln in lines:
        if cleaned and ln.strip() and ln.strip() == cleaned[-1].lstrip("#- ").strip():
            continue
        cleaned.append(ln)
    return "\n".join(cleaned).strip()


def grab(pattern, text, default=""):
    m = re.search(pattern, text, re.S)
    return html.unescape(m.group(1)).strip() if m else default


def main(raw_dir):
    os.makedirs(OUT, exist_ok=True)
    files = sorted(f for f in os.listdir(raw_dir) if f.endswith(".raw.html"))
    if not files:
        print("no .raw.html files in", raw_dir)
        return 1

    for fn in files:
        slug = fn[: -len(".raw.html")]
        h = open(os.path.join(raw_dir, fn), encoding="utf-8").read()

        title = grab(r'<h1[^>]*data-hook="post-title"[^>]*>(.*?)</h1>', h) or slug
        author = grab(r'<span data-hook="user-name">(.*?)</span>', h, "Robert Fisher")
        date = grab(r'<span title="([^"]+)" class="time-ago"', h)
        read = grab(r'<span title="([^"]+)" data-hook="time-to-read"', h, "3 min read")

        m = re.search(r"<article[^>]*>(.*?)</article>", h, re.S)
        if not m:
            print("!! no <article> in", fn)
            continue
        body_html = m.group(1)
        # Cut the header block off — everything up to and including </header>.
        hdr = re.search(r"</header>", body_html)
        if hdr:
            body_html = body_html[hdr.end():]

        body = to_markdown(body_html)
        # Trailing Wix chrome ("Comments", share prompts) sits after the prose.
        body = re.split(r"\n#+ ?(?:Comments|Share this post)\b", body)[0].strip()

        front = (
            "---\n"
            f"title: {title}\n"
            f"author: {author}\n"
            f"date: {date}\n"
            f"read_time: {read}\n"
            f"slug: {slug}\n"
            "source: imported from Wix 2026-08-17\n"
            "---\n\n"
        )
        path = os.path.join(OUT, slug + ".md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(front + body + "\n")
        print(f"{slug}: {len(body)} chars, {body.count(chr(10)+'## ')} h2")
    return 0


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(raw))

# -*- coding: utf-8 -*-
import os, json
DIR = os.path.dirname(os.path.abspath(__file__))
LOGOS = json.load(open(os.path.join(DIR, "logos.json")))

# --- reuse the tested territory widget: pull its <style> and <body> ---
w = open(os.path.join(DIR, "widget.html"), encoding="utf-8").read()
map_style = w[w.index("<style>")+7 : w.index("</style>")]
map_body  = w[w.index("<body>")+6 : w.index("</body>")]

LINES = [
 ("Soprema", "Soprema", "Building envelope &amp; waterproofing &mdash; air/vapor barriers, below-grade and above-grade waterproofing, and ALSAN liquid-applied membranes for the complete envelope."),
 ("Siplast", "Siplast", "Commercial roofing systems &mdash; SBS-modified bitumen, single-ply, and liquid-applied (PMMA) membranes."),
 ("Atlas EnergyShield", "Atlas", "Polyiso continuous wall insulation engineered for energy-code-compliant wall assemblies."),
 ("Anti-Hydro", "Anti-Hydro", "Integral concrete admixtures &mdash; waterproofing and protection dosed into the mix. Trusted since 1904."),
 ("Nox-Crete", "Nox-Crete", "Concrete chemistry &mdash; form-release, curing, and precast / tilt-up solutions, including TigerLoc."),
 ("LymTal Iso-Flex", "LymTal", "Traffic-bearing deck membranes, expansion joints, and sealants for parking structures and plazas."),
]

SYSTEMS = [
 ("Commercial Roofing", "Modified bitumen, single-ply &amp; liquid-applied membrane systems."),
 ("Building Envelope &amp; Waterproofing", "Air/vapor barriers, below-grade waterproofing &amp; deck coatings."),
 ("Wall Insulation", "Polyiso continuous insulation for energy-code wall assemblies."),
 ("Concrete Admixtures", "Integral waterproofing &amp; protection dosed into the mix."),
 ("Concrete Chemistry &amp; Precast", "Form release, curing, and precast / tilt-up solutions."),
 ("Traffic Coatings &amp; Joints", "Parking-deck membranes, expansion joints &amp; sealants."),
]

MARKETS = ["Commercial", "K-12 &amp; Higher Education", "Healthcare", "Government &amp; Municipal",
           "Multi-Family &amp; Housing", "Parking Structures", "Stadiums &amp; Arenas", "Office &amp; Mixed-Use"]

# --- build dynamic fragments ---
lines_cards = ""
for name, key, blurb in LINES:
    lines_cards += (
      '<div class="d7-card">'
      '<div class="d7-logobox"><img class="d7-logo" src="' + LOGOS[key] + '" alt="' + name + ' logo"></div>'
      '<h3>' + name + '</h3><p>' + blurb + '</p></div>'
    )

sys_cards = ""
for title, desc in SYSTEMS:
    sys_cards += '<div class="d7-sys"><h3>' + title + '</h3><p>' + desc + '</p></div>'

market_chips = "".join('<span class="d7-chip">' + m + '</span>' for m in MARKETS)

HEAD_CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0}
.d7{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:#1b2430; line-height:1.55; --accent:#0B5FA5; --ink:#1b2430; --muted:#5b6675;
  --bg2:#f4f7fa; --line:#e4e9ef}
.d7 .serif{font-family:Georgia,"Times New Roman",serif}
.d7 section{padding:56px 20px}
.d7 .inner{max-width:1080px; margin:0 auto}
.d7 h2{font-family:Georgia,"Times New Roman",serif; font-size:2rem; font-weight:600;
  letter-spacing:-.01em; margin:0 0 6px; color:var(--ink)}
.d7 .lead{color:var(--muted); font-size:1.04rem; max-width:680px; margin:0 0 30px}
.d7 .eyebrow{text-transform:uppercase; letter-spacing:.12em; font-size:.74rem; font-weight:700;
  color:var(--accent); margin:0 0 12px}
/* hero */
.d7-hero{background:linear-gradient(180deg,#0f1620,#1b2735); color:#fff; text-align:center; padding:74px 20px}
.d7-hero .eyebrow{color:#7fb2e0}
.d7-hero h1{font-family:Georgia,"Times New Roman",serif; font-weight:600; letter-spacing:-.01em;
  font-size:3rem; line-height:1.05; margin:0 0 16px}
.d7-hero p{color:#c7d2de; font-size:1.12rem; max-width:680px; margin:0 auto 28px}
.d7-btns{display:flex; gap:12px; justify-content:center; flex-wrap:wrap}
.d7-btn{display:inline-block; padding:13px 24px; border-radius:8px; font-weight:600; text-decoration:none;
  font-size:.98rem; transition:.15s; cursor:pointer; border:1px solid transparent}
.d7-btn.primary{background:var(--accent); color:#fff}
.d7-btn.primary:hover{background:#0a528d}
.d7-btn.ghost{background:transparent; color:#fff; border-color:rgba(255,255,255,.4)}
.d7-btn.ghost:hover{border-color:#fff; background:rgba(255,255,255,.08)}
/* lines */
.d7-grid{display:grid; grid-template-columns:repeat(3,1fr); gap:18px}
.d7-card{background:#fff; border:1px solid var(--line); border-radius:14px; padding:22px;
  box-shadow:0 1px 3px rgba(16,30,54,.05); transition:.15s}
.d7-card:hover{transform:translateY(-2px); box-shadow:0 8px 24px rgba(16,30,54,.09); border-color:#cdd8e3}
.d7-logobox{height:60px; display:flex; align-items:center; margin-bottom:14px}
.d7-logo{max-height:48px; max-width:170px; width:auto; object-fit:contain; object-position:left center}
.d7-card h3{margin:0 0 6px; font-size:1.12rem; color:var(--ink)}
.d7-card p{margin:0; color:var(--muted); font-size:.92rem}
/* systems */
.d7-sysgrid{display:grid; grid-template-columns:repeat(3,1fr); gap:16px}
.d7-sys{border-left:3px solid var(--accent); background:#fff; border-radius:0 12px 12px 0;
  padding:16px 18px; border-top:1px solid var(--line); border-right:1px solid var(--line); border-bottom:1px solid var(--line)}
.d7-sys h3{margin:0 0 4px; font-size:1.02rem}
.d7-sys p{margin:0 0 8px; color:var(--muted); font-size:.88rem}
.d7-tag{font-size:.72rem; font-weight:700; color:var(--accent); text-transform:uppercase; letter-spacing:.04em}
/* markets */
.d7-chips{display:flex; flex-wrap:wrap; gap:10px}
.d7-chip{background:#fff; border:1px solid var(--line); border-radius:40px; padding:9px 18px;
  font-size:.9rem; font-weight:600; color:var(--ink)}
/* contact */
.d7-contact{background:linear-gradient(180deg,#1b2735,#0f1620); color:#fff; text-align:center}
.d7-contact h2{color:#fff}
.d7-contact .lead{color:#c7d2de; margin-left:auto; margin-right:auto}
.d7-reps{display:flex; gap:26px; justify-content:center; flex-wrap:wrap; margin-top:26px; color:#c7d2de; font-size:.95rem}
.d7-reps b{color:#fff; display:block}
.d7-reps a{color:#7fb2e0; text-decoration:none}
.d7-foot{font-size:.82rem; color:var(--muted); text-align:center; padding:22px 20px; background:#0b1118}
.alt{background:var(--bg2)}
@media (max-width:880px){
  .d7-grid{grid-template-columns:1fr 1fr}
  .d7-sysgrid{grid-template-columns:1fr 1fr}
}
@media (max-width:560px){
  .d7 section{padding:42px 16px}
  .d7-hero{padding:56px 16px}
  .d7-hero h1{font-size:2.2rem}
  .d7-grid{grid-template-columns:1fr}
  .d7-sysgrid{grid-template-columns:1fr}
  .d7 h2{font-size:1.65rem}
}
"""

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>D7 Solutions - Building Envelope Systems</title>
<style>
__HEAD_CSS__
__MAP_STYLE__
</style>
</head>
<body>
<div class="d7">

  <!-- HERO -->
  <section class="d7-hero">
    <div class="inner">
      <p class="eyebrow">Manufacturers' Representative &middot; Building Envelope Systems</p>
      <h1>Peak Envelope Performance</h1>
      <p>D7 Solutions represents premier building-envelope manufacturers across the Upper Midwest &amp; Great Plains &mdash; helping architects, specifiers, and contractors build tighter, drier, longer-lasting buildings.</p>
      <div class="d7-btns">
        <a class="d7-btn primary" href="#lines">Explore Our Lines</a>
        <a class="d7-btn ghost" href="mailto:rob@d7sol.com?subject=Lunch%20%26%20Learn%20Request" target="_blank" rel="noopener">Request a Lunch &amp; Learn</a>
      </div>
    </div>
  </section>

  <!-- OUR LINES -->
  <section id="lines">
    <div class="inner">
      <p class="eyebrow">Our Lines</p>
      <h2 class="serif">Six trusted manufacturers, one local team</h2>
      <p class="lead">We represent best-in-class building-envelope brands and back them with local technical support, submittals, and service. Coverage varies by line &mdash; contact us to confirm availability for your project.</p>
      <div class="d7-grid">
        __LINES_CARDS__
      </div>
    </div>
  </section>

  <!-- SOLUTIONS BY SYSTEM -->
  <section class="alt">
    <div class="inner">
      <p class="eyebrow">Solutions by System</p>
      <h2 class="serif">Find the right product by what it has to do</h2>
      <p class="lead">Focused, best-in-class systems for every part of the envelope and below-grade scope.</p>
      <div class="d7-sysgrid">
        __SYS_CARDS__
      </div>
    </div>
  </section>

  <!-- MARKETS -->
  <section>
    <div class="inner">
      <p class="eyebrow">Markets We Serve</p>
      <h2 class="serif">Built for demanding projects</h2>
      <p class="lead">From parking structures to hospitals, our systems perform where the envelope matters most.</p>
      <div class="d7-chips">__MARKET_CHIPS__</div>
    </div>
  </section>

  <!-- TERRITORY (interactive map) -->
  <section id="territory" class="alt">
    <div class="inner">
      __MAP_BODY__
    </div>
  </section>

  <!-- CONTACT -->
  <section id="contact" class="d7-contact">
    <div class="inner">
      <p class="eyebrow">Let's Build Better</p>
      <h2 class="serif">Get a rep on your next project</h2>
      <p class="lead">Schedule a lunch &amp; learn, request product data and submittals, or talk through an assembly. We're local, responsive, and ready to help.</p>
      <div class="d7-btns">
        <a class="d7-btn primary" href="mailto:rob@d7sol.com?subject=Project%20Inquiry" target="_blank" rel="noopener">Email a Rep</a>
        <a class="d7-btn ghost" href="tel:+14027093150">Call 402.709.3150</a>
      </div>
      <div class="d7-reps">
        <div><b>David Fincham</b> President<br><a href="tel:+15152318508">515.231.8508</a> &middot; <a href="mailto:david@d7sol.com">david@d7sol.com</a></div>
        <div><b>Rob Fisher</b> Managing Director<br><a href="tel:+14027093150">402.709.3150</a> &middot; <a href="mailto:rob@d7sol.com">rob@d7sol.com</a></div>
      </div>
    </div>
  </section>

  <div class="d7-foot">Serving North Dakota, South Dakota, Minnesota, Wisconsin, Iowa, Nebraska, Kansas &amp; Missouri. Coverage varies by line.</div>

</div>
</body>
</html>
"""

html = (html
        .replace("__HEAD_CSS__", HEAD_CSS)
        .replace("__MAP_STYLE__", map_style)
        .replace("__LINES_CARDS__", lines_cards)
        .replace("__SYS_CARDS__", sys_cards)
        .replace("__MARKET_CHIPS__", market_chips)
        .replace("__MAP_BODY__", map_body))

out = os.path.join(DIR, "homepage.html")
open(out, "w", encoding="utf-8").write(html)
print("Wrote", out, len(html), "bytes")
nb = sum(1 for b in html.encode("utf-8") if b > 127)
print("non-ASCII bytes:", nb)

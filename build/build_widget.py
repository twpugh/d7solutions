# -*- coding: utf-8 -*-
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(DIR, "paths.json")))
vb = P["viewBox"]; S = P["states"]
LOGOS = json.load(open(os.path.join(DIR, "logos.json")))

STATE_NAMES = {"ND":"North Dakota","SD":"South Dakota","MN":"Minnesota","WI":"Wisconsin",
               "IA":"Iowa","NE":"Nebraska","KS":"Kansas","MO":"Missouri"}

# Authoritative territory per Rob Fisher, 2026-06-03
TERR = [
  ("Soprema",    "Building envelope &amp; waterproofing",   ["ND","SD","MN","WI","IA","NE"], "#C8102E"),
  ("Atlas",      "Polyiso wall insulation",                 ["ND","SD","MN","IA","NE"],      "#0F8A4F"),
  ("Anti-Hydro", "Integral concrete admixtures",            ["ND","SD","MN","IA","NE"],      "#6A2C91"),
  ("Nox-Crete",  "Concrete chemistry &amp; precast",        ["ND","SD","MN","IA","NE"],      "#E8742C"),
  ("LymTal",     "Traffic coatings &amp; expansion joints", ["IA","NE"],                     "#008FB3"),
]

ORDER = ["ND","SD","MN","WI","IA","NE","KS","MO"]

# Build SVG state paths + labels
paths = []
labels = []
for ab in ORDER:
    s = S[ab]
    paths.append(f'<path id="st-{ab}" class="state" data-ab="{ab}" d="{s["d"]}"></path>')
    labels.append(f'<text class="lbl" id="lbl-{ab}" x="{s["cx"]}" y="{s["cy"]}">{ab}</text>')
paths_svg = "\n      ".join(paths)
labels_svg = "\n      ".join(labels)

# JS data
terr_js = ",\n  ".join(
    f'{{name:"{n}",cat:"{c}",states:{json.dumps(st)},color:"{col}",logo:{json.dumps(LOGOS[n])}}}'
    for (n,c,st,col) in TERR
)
names_js = json.dumps(STATE_NAMES)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>D7 Solutions - Territory Map</title>
<style>
  *{{box-sizing:border-box}}
  :root{{
    --ink:#1f2733; --muted:#5a6573; --line:#ffffff;
    --base:#e7ecf1; --baseStroke:#c9d3dd; --foot:#d7e3ee; --accent:#0B5FA5;
    --card:#ffffff; --shadow:0 1px 3px rgba(16,30,54,.08),0 4px 16px rgba(16,30,54,.06);
  }}
  html,body{{margin:0;padding:0}}
  .wrap{{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    color:var(--ink); max-width:980px; margin:0 auto; padding:18px;
  }}
  .head{{text-align:center; margin-bottom:14px}}
  .head h2{{margin:0 0 4px; font-size:1.55rem; letter-spacing:-.01em}}
  .head p{{margin:0; color:var(--muted); font-size:.95rem}}
  .layout{{display:flex; gap:22px; align-items:flex-start}}
  .controls{{flex:0 0 280px; display:flex; flex-direction:column; gap:8px}}
  .mfr{{
    display:flex; flex-direction:column; gap:1px; text-align:left; cursor:pointer;
    background:var(--card); border:1px solid #e3e8ee; border-left:5px solid var(--c);
    border-radius:10px; padding:10px 12px; box-shadow:var(--shadow); transition:.15s;
    font:inherit; color:inherit; width:100%;
  }}
  .mfr:hover{{transform:translateY(-1px); border-color:var(--c)}}
  .mfr .mlogo{{height:30px; max-width:178px; width:auto; object-fit:contain; object-position:left center; display:block; margin:1px 0 6px}}
  .mfr .ct{{font-size:.78rem; color:var(--muted); line-height:1.25}}
  .mfr .ns{{font-size:.72rem; color:var(--muted); margin-top:3px; font-variant:all-small-caps; letter-spacing:.03em}}
  .mfr[aria-pressed="true"]{{border-color:var(--c);
    box-shadow:0 0 0 2px var(--c) inset, var(--shadow);
    background:linear-gradient(rgba(255,255,255,.90),rgba(255,255,255,.90)), var(--c)}}
  .stage{{flex:1 1 auto; min-width:0}}
  svg{{width:100%; height:auto; display:block}}
  .state{{fill:var(--base); stroke:var(--line); stroke-width:1.6; transition:fill .18s; cursor:pointer}}
  .state.foot{{fill:var(--foot)}}
  .state.on{{fill:var(--hl)}}
  .lbl{{font:600 15px -apple-system,Segoe UI,Roboto,sans-serif; fill:var(--muted);
        text-anchor:middle; dominant-baseline:central; pointer-events:none; transition:fill .18s}}
  .lbl.on{{fill:#fff}}
  .cap{{margin-top:10px; min-height:42px; background:#f6f8fb; border:1px solid #e7edf3;
        border-radius:10px; padding:10px 14px; font-size:.9rem}}
  .cap b{{color:var(--ink)}}
  .cap .sw{{display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; vertical-align:middle}}
  .foot-note{{margin-top:12px; color:var(--muted); font-size:.8rem; text-align:center; line-height:1.4}}
  .reset{{align-self:flex-start; margin-top:4px; background:none; border:1px dashed #c2ccd6;
          color:var(--muted); border-radius:8px; padding:7px 12px; cursor:pointer; font:inherit; font-size:.82rem; width:100%}}
  .reset:hover{{border-color:var(--accent); color:var(--accent)}}
  @media (max-width:720px){{
    .wrap{{padding:14px}}
    .head h2{{font-size:1.4rem}}
    .head p{{font-size:.88rem}}
    .layout{{flex-direction:column; gap:13px}}
    /* compact logo tiles above the map; details move to the caption.
       auto-fit picks 2 cols on narrower phones, 3 on wider ones (e.g. Pixel 8 Pro). */
    .controls{{flex:1 1 auto; width:100%; display:grid;
      grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px}}
    .mfr{{align-items:center; justify-content:center; padding:10px 8px; min-height:56px; border-left-width:4px}}
    .mfr .mlogo{{height:28px; max-width:100%; margin:0; object-position:center}}
    .mfr .ct, .mfr .ns{{display:none}}
    .reset{{grid-column:1 / -1}}
    .cap{{min-height:54px}}
    /* cap the map height on phones so the widget stays compact (keeps aspect, centers) */
    .stage svg{{max-height:360px; width:auto; max-width:100%; margin:0 auto}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <h2>Our Territory</h2>
    <p>Click a manufacturer to see the states we represent. Click a state to see its lines.</p>
  </div>
  <div class="layout">
    <div class="controls" id="controls"></div>
    <div class="stage">
      <svg viewBox="0 0 {vb[0]} {vb[1]}" role="img" aria-label="Map of D7 Solutions territory">
      {paths_svg}
      {labels_svg}
      </svg>
      <div class="cap" id="cap"></div>
      <div class="foot-note">
        D7 Solutions&rsquo; footprint spans 8 states &mdash; North Dakota, South Dakota, Minnesota, Wisconsin, Iowa, Nebraska, Kansas &amp; Missouri.<br>
        Coverage varies by line. Don&rsquo;t see your state for a product? <strong>Contact us</strong> &mdash; our territory is growing.
      </div>
    </div>
  </div>
</div>
<script>
  var TERR=[
  {terr_js}
  ];
  var NAMES={names_js};
  var FOOT=["ND","SD","MN","WI","IA","NE","KS","MO"];
  var states=document.querySelectorAll('.state');
  var labels=document.querySelectorAll('.lbl');
  var cap=document.getElementById('cap');
  var controls=document.getElementById('controls');
  var active=null;

  function clearMap(){{
    states.forEach(function(s){{s.classList.remove('on'); s.style.removeProperty('--hl');}});
    labels.forEach(function(l){{l.classList.remove('on');}});
  }}
  function setFootprint(){{
    states.forEach(function(s){{ s.classList.toggle('foot', FOOT.indexOf(s.dataset.ab)>=0); }});
  }}
  function listStates(abbrs){{
    return abbrs.map(function(a){{return NAMES[a];}}).join(', ');
  }}
  function selectMfr(i){{
    active=i; var m=TERR[i];
    clearMap();
    document.querySelectorAll('.mfr').forEach(function(b,j){{b.setAttribute('aria-pressed', j===i?'true':'false');}});
    m.states.forEach(function(a){{
      var st=document.getElementById('st-'+a), lb=document.getElementById('lbl-'+a);
      if(st){{st.style.setProperty('--hl', m.color); st.classList.add('on');}}
      if(lb){{lb.classList.add('on');}}
    }});
    cap.innerHTML='<span class="sw" style="background:'+m.color+'"></span><b>'+m.name+'</b> &mdash; '
      + m.states.length + ' state'+(m.states.length>1?'s':'')+': '+listStates(m.states);
  }}
  function selectState(ab){{
    var lines=TERR.filter(function(m){{return m.states.indexOf(ab)>=0;}}).map(function(m){{return m.name;}});
    if(lines.length){{
      cap.innerHTML='<b>'+NAMES[ab]+'</b> &mdash; available lines: '+lines.join(', ');
    }} else {{
      cap.innerHTML='<b>'+NAMES[ab]+'</b> &mdash; in our footprint; no lines contracted yet. <strong>Contact us.</strong>';
    }}
  }}
  function reset(){{
    active=null; clearMap();
    document.querySelectorAll('.mfr').forEach(function(b){{b.setAttribute('aria-pressed','false');}});
    cap.innerHTML='<b>D7 Solutions</b> &mdash; representing premier building-envelope lines across the Upper Midwest &amp; Great Plains. Select a manufacturer above.';
  }}

  // build manufacturer buttons
  TERR.forEach(function(m,i){{
    var b=document.createElement('button');
    b.className='mfr'; b.style.setProperty('--c', m.color); b.setAttribute('aria-pressed','false');
    b.setAttribute('aria-label', m.name);
    b.innerHTML='<img class="mlogo" src="'+m.logo+'" alt="'+m.name+'">'
      +'<span class="ct">'+m.cat+'</span>'
      +'<span class="ns">'+m.states.join(' &middot; ')+'</span>';
    b.addEventListener('click', function(){{ selectMfr(i); }});
    controls.appendChild(b);
  }});
  var rb=document.createElement('button'); rb.className='reset'; rb.textContent='Show all / reset';
  rb.addEventListener('click', reset); controls.appendChild(rb);

  states.forEach(function(s){{ s.addEventListener('click', function(){{ selectState(s.dataset.ab); }}); }});

  setFootprint();
  reset();
</script>
</body>
</html>
"""

out = os.path.join(DIR, "widget.html")
open(out, "w", encoding="utf-8").write(html)
print("Wrote", out, len(html), "bytes")

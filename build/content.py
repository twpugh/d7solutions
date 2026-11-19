# -*- coding: utf-8 -*-
"""Single source of truth for D7 Solutions site content.

Everything a non-developer would want to change lives here, not in the
templates. Territory and line positioning are Rob Fisher's, 2026-06-03 —
see the LINE POSITIONING rule below before editing any `blurb`.
"""

SITE = {
    "name": "D7 Solutions",
    "tagline": "Peak Envelope Performance",
    "domain": "d7solutions.net",
    "base_url": "https://www.d7solutions.net",
    "description": (
        "D7 Solutions is an independent manufacturers' representative for premier "
        "building-envelope systems across the Upper Midwest and Great Plains."
    ),
    "accent": "#0B5FA5",
    "founded": 2026,
}

CONTACTS = [
    {
        "name": "David Fincham",
        "title": "President",
        "phone": "515.231.8508",
        "phone_href": "+15152318508",
        "email": "david@d7sol.com",
        "photo": None,
    },
    {
        "name": "Rob Fisher",
        "title": "Managing Director",
        "phone": "402.709.3150",
        "phone_href": "+14027093150",
        "email": "rob@d7sol.com",
        "photo": "/assets/img/rob-fisher.jpg",
    },
]

# LINE POSITIONING (Rob Fisher, 2026-06-03) — IMPORTANT:
# ONE lane per line. Do NOT advertise where lines cross over each other.
# Editing a blurb to add an overlapping capability is a commercial decision,
# not a copy tweak.
LINES = [
    {
        "name": "Soprema",
        "slug": "soprema",
        "lane": "Building Envelope & Waterproofing",
        "logo": "/assets/logos/Soprema.png",
        "color": "#C8102E",
        "blurb": (
            "Air/vapor barriers, below-grade and above-grade waterproofing, and "
            "ALSAN liquid-applied membranes for the complete envelope."
        ),
        "detail": (
            "Soprema is D7's building-envelope and waterproofing line — the "
            "weather-control layers that keep air and water out of the assembly. "
            "SBS-modified bitumen air and vapor barriers, self-adhered and "
            "torch-applied below-grade waterproofing, and the ALSAN family of "
            "liquid-applied membranes for details, decks and restoration."
        ),
        "states": ["ND", "SD", "MN", "WI", "IA", "NE"],
    },
    # SIPLAST REMOVED 2026-08-17 (Rob): D7 does NOT rep Siplast. It had been
    # carried from the June draft as "territory in progress". Do not re-add a
    # line here on the strength of a negotiation — only a signed rep agreement.
    {
        "name": "Atlas EnergyShield",
        "slug": "atlas-energyshield",
        "lane": "Wall Insulation",
        "logo": "/assets/logos/Atlas.png",
        "color": "#0F8A4F",
        "blurb": "Polyiso continuous wall insulation engineered for energy-code-compliant wall assemblies.",
        "detail": (
            "Atlas EnergyShield is D7's polyiso continuous-insulation line for "
            "walls. Foil- and coated-glass-faced polyiso boards that carry the "
            "continuous-insulation R-value the energy code asks for, detailed to "
            "work with the air barrier rather than against it."
        ),
        "states": ["ND", "SD", "MN", "IA", "NE"],
    },
    {
        "name": "Anti-Hydro",
        "slug": "anti-hydro",
        "lane": "Concrete Admixtures",
        "logo": "/assets/logos/Anti-Hydro.png",
        "color": "#6A2C91",
        "blurb": "Integral concrete admixtures — waterproofing and protection dosed into the mix. Trusted since 1904.",
        "detail": (
            "Anti-Hydro is D7's integral concrete admixture line — "
            "waterproofing and protection dosed into the mix rather than applied "
            "to the surface afterward. Water-resisting, corrosion-inhibiting and "
            "shrinkage-compensating admixtures for structural and architectural "
            "concrete."
        ),
        "states": ["ND", "SD", "MN", "IA", "NE"],
    },
    {
        "name": "Nox-Crete",
        "slug": "nox-crete",
        "lane": "Concrete Chemistry & Precast",
        "logo": "/assets/logos/Nox-Crete.png",
        "color": "#E8742C",
        "blurb": "Form-release, curing, and precast / tilt-up solutions, including TigerLoc.",
        "detail": (
            "Nox-Crete is D7's concrete chemistry line for the plant and the "
            "pour — form-release agents, cures and sealers, bond breakers, "
            "and the TigerLoc system for precast and tilt-up work."
        ),
        "states": ["ND", "SD", "MN", "IA", "NE"],
    },
    {
        "name": "LymTal Iso-Flex",
        "slug": "lymtal-iso-flex",
        "lane": "Traffic Coatings & Joints",
        "logo": "/assets/logos/LymTal.png",
        "color": "#008FB3",
        "blurb": "Traffic-bearing deck membranes, expansion joints, and sealants for parking structures and plazas.",
        "detail": (
            "LymTal Iso-Flex is D7's traffic-coating and expansion-joint line. "
            "Traffic-bearing deck membranes, Iso-Flex expansion joint systems and "
            "sealants for parking structures, plazas and other decks that carry "
            "wheels as well as weather."
        ),
        "states": ["IA", "NE"],
    },
]

# Every system here must be backed by a line in LINES. "Commercial Roofing" was
# removed with Siplast — advertising a system D7 has no product for is the same
# overclaim as advertising a line it doesn't rep.
SYSTEMS = [
    ("Building Envelope & Waterproofing", "Air/vapor barriers, below-grade waterproofing & deck coatings."),
    ("Wall Insulation", "Polyiso continuous insulation for energy-code wall assemblies."),
    ("Concrete Admixtures", "Integral waterproofing & protection dosed into the mix."),
    ("Concrete Chemistry & Precast", "Form release, curing, and precast / tilt-up solutions."),
    ("Traffic Coatings & Joints", "Parking-deck membranes, expansion joints & sealants."),
]

MARKETS = [
    "Commercial", "K-12 & Higher Education", "Healthcare", "Government & Municipal",
    "Multi-Family & Housing", "Parking Structures", "Stadiums & Arenas", "Office & Mixed-Use",
]

STATE_NAMES = {
    "ND": "North Dakota", "SD": "South Dakota", "MN": "Minnesota", "WI": "Wisconsin",
    "IA": "Iowa", "NE": "Nebraska",
}
# Kansas and Missouri removed 2026-11-19 (Wayne): not shown on the map or table.
# The territory table orders its columns by coverage (most lines first); see
# build.py. This list is the tie-break order and the map/footer order.
STATE_ORDER = ["ND", "SD", "MN", "WI", "IA", "NE"]

NAV = [
    ("Home", "/"),
    ("Our Lines", "/lines/"),
    ("Territory", "/territory/"),
    ("Insights", "/blog/"),
    ("Contact", "/contact/"),
]

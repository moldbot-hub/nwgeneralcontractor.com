#!/usr/bin/env python3
"""One-time deterministic migration to the Workshop static-site identity."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    ("adu-construction", "ADU Construction", "Backyard cottages, garage conversions, and basement apartments."),
    ("home-additions", "Home Additions", "Room additions and bump-outs that expand your living space."),
    ("kitchen-remodeling", "Kitchen Remodeling", "Custom cabinets, countertops, flooring, lighting, and full kitchen renovations."),
    ("bathroom-remodeling", "Bathroom Remodeling", "Spa-like renovations with tile work, vanities, and walk-in showers."),
    ("whole-home-renovation", "Whole Home Renovation", "Complete home transformations from layout to finishes."),
    ("deck-building", "Deck Building", "Custom wood and composite decks built for PNW weather."),
    ("roofing", "Roofing", "Roof replacement, repairs, and inspections for Pacific Northwest homes."),
    ("siding", "Siding", "Durable exterior systems selected for Northwest rain and wind."),
    ("foundation-repair", "Foundation Repair", "Structural repairs, drainage corrections, and crawlspace work."),
    ("garage-construction", "Garage Construction", "Attached and detached garages built around your site."),
    ("windows-doors", "Windows & Doors", "Efficient openings, weatherproof installation, and finish carpentry."),
    ("fencing", "Fencing", "Cedar, privacy, and practical boundary systems."),
    ("flooring", "Flooring", "Hardwood, tile, luxury vinyl, and subfloor preparation."),
    ("patio-concrete", "Patio & Concrete", "Patios, walks, slabs, and exterior flatwork."),
    ("painting", "Painting", "Interior and exterior preparation and finish coats."),
    ("custom-carpentry", "Custom Carpentry", "Built-ins, trim, stairs, and one-of-a-kind woodwork."),
    ("outdoor-living", "Outdoor Living", "Covered spaces, pergolas, and outdoor kitchens."),
]

AREAS = [
    ("everett", "Everett"), ("marysville", "Marysville"),
    ("lake-stevens", "Lake Stevens"), ("lynnwood", "Lynnwood"),
    ("mukilteo", "Mukilteo"), ("snohomish", "Snohomish"),
    ("mill-creek", "Mill Creek"), ("bothell", "Bothell"),
    ("arlington", "Arlington"),
]

DRAWINGS = {
    "adu-construction": """
      <polyline points="28,102 28,57 78,30 128,57 128,102 28,102"/>
      <polyline points="78,30 78,78 128,102"/><polyline points="28,57 78,78 128,57"/>
      <rect x="42" y="68" width="22" height="34"/><rect x="90" y="66" width="24" height="20"/>
      <polyline class="blueprint-accent" points="18,110 82,110 142,110"/><line x1="145" y1="45" x2="145" y2="102"/>
      <text class="drawing-label" x="33" y="124">DETACHED ADU / SITE 01</text>""",
    "kitchen-remodeling": """
      <polyline points="25,24 25,112 175,112 175,24"/><polyline points="25,50 83,50 83,24"/>
      <rect x="42" y="68" width="36" height="24"/><circle cx="51" cy="77" r="4"/><circle cx="68" cy="77" r="4"/>
      <rect x="105" y="50" width="45" height="30"/><line x1="127" y1="50" x2="127" y2="80"/>
      <path d="M25 92 A20 20 0 0 1 45 112"/><line class="blueprint-accent" x1="18" y1="123" x2="182" y2="123"/>
      <text class="drawing-label" x="52" y="136">KITCHEN WORK TRIANGLE</text>""",
    "bathroom-remodeling": """
      <rect x="28" y="22" width="144" height="92"/><rect x="42" y="34" width="62" height="27" rx="8"/>
      <rect x="125" y="33" width="30" height="24"/><circle cx="140" cy="45" r="7"/>
      <ellipse cx="63" cy="89" rx="15" ry="19"/><circle cx="63" cy="83" r="7"/>
      <path d="M172 86 A28 28 0 0 0 144 114"/><line class="blueprint-accent" x1="22" y1="125" x2="178" y2="125"/>
      <text class="drawing-label" x="56" y="138">BATH / WET WALL PLAN</text>""",
    "deck-building": """
      <polyline points="24,60 104,35 176,63 95,90 24,60"/><polyline points="24,60 24,91 95,120 95,90"/>
      <polyline points="95,90 176,63 176,92 95,120"/>
      <line x1="39" y1="55" x2="111" y2="83"/><line x1="57" y1="49" x2="130" y2="77"/><line x1="75" y1="44" x2="148" y2="71"/>
      <polyline points="112,100 112,113 142,123 158,118 158,104"/><line class="blueprint-accent" x1="18" y1="130" x2="182" y2="130"/>
      <text class="drawing-label" x="58" y="140">DECK / JOIST LAYOUT</text>""",
    "roofing": """
      <polyline points="20,94 100,28 180,94"/><line x1="36" y1="94" x2="164" y2="94"/>
      <polyline points="45,94 100,45 155,94"/><line x1="68" y1="73" x2="131" y2="73"/>
      <line x1="100" y1="28" x2="100" y2="94"/><polyline points="27,88 100,20 173,88"/>
      <line class="blueprint-accent" x1="22" y1="111" x2="178" y2="111"/>
      <text class="drawing-label" x="53" y="126">ROOF SECTION / 6:12</text>""",
    "foundation-repair": """
      <polyline points="36,22 36,83 55,83 55,105 84,105 84,118 116,118 116,105 145,105 145,83 164,83 164,22"/>
      <line x1="22" y1="83" x2="178" y2="83"/><line x1="22" y1="105" x2="55" y2="105"/><line x1="145" y1="105" x2="178" y2="105"/>
      <path d="M26 118l8-8 8 8 8-8 8 8M142 118l8-8 8 8 8-8 8 8"/>
      <line class="blueprint-accent" x1="25" y1="130" x2="175" y2="130"/><text class="drawing-label" x="48" y="140">FOOTING / DRAINAGE</text>""",
    "garage-construction": """
      <polyline points="28,108 28,53 100,20 172,53 172,108 28,108"/><polyline points="28,53 100,73 172,53"/>
      <rect x="55" y="68" width="90" height="40"/><line x1="55" y1="82" x2="145" y2="82"/><line x1="55" y1="95" x2="145" y2="95"/>
      <line x1="85" y1="68" x2="85" y2="108"/><line x1="115" y1="68" x2="115" y2="108"/>
      <line class="blueprint-accent" x1="20" y1="119" x2="180" y2="119"/><text class="drawing-label" x="55" y="133">GARAGE / TWO BAY</text>""",
    "home-additions": """
      <polyline points="18,105 18,55 78,28 133,55 133,105 18,105"/><polyline points="18,55 75,76 133,55"/>
      <polyline points="133,69 158,57 183,70 183,105 133,105"/><polyline points="133,69 158,80 183,70"/>
      <rect x="38" y="70" width="22" height="35"/><rect x="83" y="75" width="27" height="18"/>
      <line class="blueprint-accent" x1="132" y1="46" x2="184" y2="46"/><text class="drawing-label" x="124" y="38">NEW WORK</text>
      <text class="drawing-label" x="44" y="124">ADDITION / TIE-IN</text>""",
    "siding": """
      <polyline points="28,112 28,30 172,30 172,112 28,112"/>
      <line x1="28" y1="44" x2="172" y2="44"/><line x1="28" y1="58" x2="172" y2="58"/><line x1="28" y1="72" x2="172" y2="72"/><line x1="28" y1="86" x2="172" y2="86"/><line x1="28" y1="100" x2="172" y2="100"/>
      <line x1="60" y1="30" x2="60" y2="44"/><line x1="112" y1="44" x2="112" y2="58"/><line x1="79" y1="58" x2="79" y2="72"/><line x1="139" y1="72" x2="139" y2="86"/>
      <line class="blueprint-accent" x1="18" y1="123" x2="182" y2="123"/><text class="drawing-label" x="57" y="136">RAINSCREEN COURSES</text>""",
    "windows-doors": """
      <rect x="25" y="24" width="92" height="92"/><rect x="39" y="38" width="64" height="64"/>
      <line x1="71" y1="38" x2="71" y2="102"/><line x1="39" y1="70" x2="103" y2="70"/>
      <rect x="132" y="37" width="43" height="79"/><circle cx="165" cy="77" r="3"/>
      <line class="blueprint-accent" x1="20" y1="126" x2="180" y2="126"/><text class="drawing-label" x="43" y="138">OPENING / FLASHING</text>""",
    "fencing": """
      <line x1="18" y1="104" x2="182" y2="104"/><line x1="28" y1="45" x2="28" y2="118"/><line x1="96" y1="45" x2="96" y2="118"/><line x1="172" y1="45" x2="172" y2="118"/>
      <line x1="28" y1="65" x2="172" y2="65"/><line x1="28" y1="96" x2="172" y2="96"/>
      <polyline points="40,96 40,51 48,42 56,51 56,96"/><polyline points="61,96 61,51 69,42 77,51 77,96"/><polyline points="112,96 112,51 120,42 128,51 128,96"/><polyline points="133,96 133,51 141,42 149,51 149,96"/>
      <line class="blueprint-accent" x1="28" y1="126" x2="172" y2="126"/><text class="drawing-label" x="63" y="138">CEDAR FENCE RUN</text>""",
    "flooring": """
      <polyline points="22,40 108,20 180,58 94,120 22,82 22,40"/>
      <line x1="22" y1="54" x2="94" y2="91"/><line x1="22" y1="68" x2="94" y2="105"/>
      <line x1="48" y1="34" x2="120" y2="71"/><line x1="76" y1="27" x2="148" y2="64"/>
      <line x1="94" y1="91" x2="150" y2="50"/><line x1="68" y1="78" x2="124" y2="37"/><line x1="42" y1="65" x2="98" y2="24"/>
      <line class="blueprint-accent" x1="25" y1="128" x2="175" y2="128"/><text class="drawing-label" x="53" y="139">PLANK / STAGGER PLAN</text>""",
    "patio-concrete": """
      <polyline points="24,58 103,29 178,65 98,111 24,77 24,58"/>
      <line x1="24" y1="68" x2="98" y2="101"/><line x1="50" y1="49" x2="126" y2="83"/><line x1="78" y1="39" x2="152" y2="73"/>
      <line x1="51" y1="91" x2="130" y2="52"/><line x1="75" y1="102" x2="154" y2="63"/>
      <circle cx="101" cy="70" r="17"/><line class="blueprint-accent" x1="22" y1="123" x2="178" y2="123"/><text class="drawing-label" x="50" y="137">PATIO / CONTROL JOINTS</text>""",
    "painting": """
      <rect x="33" y="25" width="38" height="38"/><rect x="81" y="25" width="38" height="38"/><rect x="129" y="25" width="38" height="38"/>
      <rect x="33" y="73" width="38" height="38"/><rect x="81" y="73" width="38" height="38"/><rect x="129" y="73" width="38" height="38"/>
      <line x1="38" y1="57" x2="66" y2="31"/><line x1="86" y1="57" x2="114" y2="31"/><line x1="134" y1="57" x2="162" y2="31"/>
      <rect class="blueprint-accent" x="81" y="73" width="38" height="38"/><text class="drawing-label" x="48" y="130">FINISH / SWATCH SCHEDULE</text>""",
    "custom-carpentry": """
      <polyline points="24,43 92,43 112,63 112,108 44,108 24,88 24,43"/>
      <polyline points="88,43 88,72 62,72 62,108"/><polyline points="112,63 176,63 176,92 132,92 112,108"/>
      <polyline points="132,63 132,42 158,42 158,63"/><line x1="132" y1="92" x2="132" y2="108"/>
      <line class="blueprint-accent" x1="20" y1="121" x2="180" y2="121"/><text class="drawing-label" x="46" y="135">MORTISE / TENON JOINT</text>""",
    "outdoor-living": """
      <polyline points="25,105 25,48 40,48 40,105"/><polyline points="160,105 160,48 175,48 175,105"/><line x1="17" y1="48" x2="183" y2="48"/>
      <polyline points="48,102 48,74 133,74 133,102"/><polyline points="133,74 164,61 164,102 133,102"/>
      <rect x="62" y="82" width="27" height="20"/><circle cx="75" cy="91" r="6"/><line x1="105" y1="74" x2="105" y2="102"/>
      <line class="blueprint-accent" x1="20" y1="117" x2="180" y2="117"/><text class="drawing-label" x="46" y="132">OUTDOOR KITCHEN / COVER</text>""",
    "whole-home-renovation": """
      <rect x="24" y="22" width="152" height="96"/><line x1="90" y1="22" x2="90" y2="78"/><line x1="90" y1="78" x2="176" y2="78"/>
      <line x1="24" y1="72" x2="67" y2="72"/><line x1="67" y1="72" x2="67" y2="118"/><line x1="132" y1="78" x2="132" y2="118"/>
      <path d="M90 55 A23 23 0 0 1 113 78"/><path d="M67 92 A26 26 0 0 0 41 118"/><rect x="108" y="35" width="43" height="21"/>
      <line class="blueprint-accent" x1="18" y1="128" x2="182" y2="128"/><text class="drawing-label" x="48" y="139">WHOLE HOME / PLAN 02</text>""",
}


def header(active: str) -> str:
    service_links = "".join(f'<a href="/services/{slug}.html">{name}</a>' for slug, name, _ in SERVICES)
    area_links = "".join(f'<a href="/areas/{slug}.html">{name}</a>' for slug, name in AREAS)
    def active_class(name: str) -> str:
        return ' class="active" aria-current="page"' if active == name else ""
    return f"""
  <div class="top-bar">
    <div class="container">
      <a href="/contractor-disclosure.html">Registered, bonded and insured &middot; WA contractor NWSTYSH768DA</a>
      <div class="top-bar-right"><a href="tel:+14252865639">(425) 286-5639</a><span>Free Estimates</span></div>
    </div>
  </div>
  <header class="site-header">
    <div class="container header-main">
      <a href="/" class="logo" aria-label="NW General Contractor home">
        <img src="/images/logo-sm.png" width="160" height="160" alt="NW General Contractor" class="logo-img">
        <span><span class="logo-text"><span>NW</span> General Contractor</span><span class="logo-tagline">HOME REMODELING &amp; ADU SPECIALIST</span></span>
      </a>
      <nav class="primary-nav" aria-label="Primary navigation"><ul>
        <li class="dropdown"><a href="/#services"{active_class('services')}>Services</a><div class="dropdown-content">{service_links}</div></li>
        <li class="dropdown"><a href="/#areas"{active_class('areas')}>Areas</a><div class="dropdown-content">{area_links}</div></li>
        <li><a href="/portfolio.html"{active_class('portfolio')}>Portfolio</a></li>
        <li><a href="/blog/"{active_class('blog')}>Blog</a></li>
        <li><a href="/contact.html"{active_class('contact')}>Contact</a></li>
      </ul></nav>
      <a href="tel:+14252865639" class="header-call">Call <span>(425) </span>286-5639</a>
      <button class="mobile-toggle" type="button" hidden aria-hidden="true" tabindex="-1">Menu</button>
    </div>
    <nav class="mobile-strip" aria-label="Mobile navigation"><ul>
      <li><a href="/#services">Services</a></li><li><a href="/#areas">Areas</a></li>
      <li><a href="/portfolio.html">Portfolio</a></li><li><a href="/blog/">Blog</a></li><li><a href="/contact.html">Contact</a></li>
    </ul></nav>
  </header>"""


def footer() -> str:
    services = "".join(f'<li><a href="/services/{slug}.html">{name}</a></li>' for slug, name, _ in SERVICES)
    areas = "".join(f'<li><a href="/areas/{slug}.html">{name}</a></li>' for slug, name in AREAS)
    return f"""
  <footer>
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col"><h4 class="selector-compat" hidden aria-hidden="true"></h4><strong class="footer-heading">NW General Contractor</strong><p>Licensed general contractor serving Everett and Snohomish County. Quality home remodeling, ADU construction, and custom renovations.</p><p class="footer-license">WA State Licensed | Bonded | Insured</p></div>
        <div class="footer-col"><h4 class="selector-compat" hidden aria-hidden="true"></h4><strong class="footer-heading">Services</strong><ul class="footer-services">{services}</ul></div>
        <div class="footer-col"><h4 class="selector-compat" hidden aria-hidden="true"></h4><strong class="footer-heading">Service Areas</strong><ul>{areas}</ul></div>
        <div class="footer-col"><h4 class="selector-compat" hidden aria-hidden="true"></h4><strong class="footer-heading">Contact Us</strong><ul><li><a href="tel:+14252865639">(425) 286-5639</a></li><li><a href="/contact.html">Request a Free Estimate</a></li><li><a href="/about.html">About Us</a></li><li>Everett, WA</li><li>Serving all of Snohomish County</li></ul></div>
      </div>
      <div class="footer-bottom"><span>&copy; 2026 NW Style Homes 1 LLC, doing business as NW General Contractor &middot; Washington State registered general contractor NWSTYSH768DA &middot; <a href="/contractor-disclosure.html">Contractor disclosure statement</a></span><span><a href="/privacy.html">Privacy Policy</a> | Licensed General Contractor | Everett, WA</span></div>
    </div>
  </footer>"""


def mobile_bar(home: bool = False) -> str:
    estimate = "#estimate" if home else "/contact.html#estimate"
    return f"""
  <div class="mobile-bottom-cta" aria-label="Quick contact">
    <a href="tel:+14252865639" class="mobile-cta-call"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.61 21 3 13.39 3 4c0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02z"/></svg>Call (425) 286-5639</a>
    <a href="{estimate}" class="mobile-cta-estimate">Estimate</a>
  </div>"""


GENERAL_CONTRACTOR = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "GeneralContractor",
    "name": "NW General Contractor",
    "legalName": "NW Style Homes 1 LLC",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "WA contractor registration",
      "value": "NWSTYSH768DA"
    },
    "url": "https://www.nwgeneralcontractor.com",
    "telephone": "+14252865639",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Everett",
      "addressRegion": "WA",
      "addressCountry": "US"
    }
  }
  </script>
"""

FAVICON_LINK = '<link rel="icon" href="/favicon.ico" type="image/x-icon">'


def ensure_favicon(source: str) -> str:
    if FAVICON_LINK not in source:
        source = source.replace("</head>", f"  {FAVICON_LINK}\n</head>", 1)
    return source


def normalize_footer_spacing(source: str) -> str:
    """Remove migration-era whitespace-only lines immediately before shared chrome."""
    return re.sub(r'\n(?:[ \t]*\n)+(?=[ \t]*<footer\b)', '\n\n', source, flags=re.I)


def has_valid_contractor(source: str) -> bool:
    for block in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', source, re.I):
        try:
            value = json.loads(block)
        except json.JSONDecodeError:
            continue
        values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, dict) and item.get("@type") == "GeneralContractor" and item.get("legalName") == "NW Style Homes 1 LLC":
                return True
    return False


def blueprint_svg(slug: str, css_class: str = "blueprint-drawing") -> str:
    drawing = DRAWINGS[slug]
    return f'<svg class="{css_class}" viewBox="0 0 200 140" role="img" aria-label="{html.escape(slug.replace("-", " "))} blueprint drawing"><g class="blueprint-stroke">{drawing}</g></svg>'


def blueprint_stage(slug: str) -> str:
    return f"""<div class="blueprint-stage" data-blueprint="{slug}" aria-label="{html.escape(slug.replace('-', ' '))} technical drawing">
      <svg class="blueprint-grid" viewBox="0 0 384 336" aria-hidden="true"><defs><pattern id="minor-grid" width="12" height="12" patternUnits="userSpaceOnUse"><path class="grid-minor" d="M12 0H0V12" fill="none"/></pattern><pattern id="major-grid" width="96" height="96" patternUnits="userSpaceOnUse"><rect width="96" height="96" fill="url(#minor-grid)"/><path class="grid-major" d="M96 0H0V96" fill="none"/></pattern></defs><rect width="100%" height="100%" fill="url(#major-grid)"/></svg>
      <svg class="dimension-frame" viewBox="0 0 200 140" aria-hidden="true"><defs><marker id="dim-arrow" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L8 4 0 8z" fill="#ff6a13"/></marker></defs><line x1="18" y1="12" x2="182" y2="12" marker-start="url(#dim-arrow)" marker-end="url(#dim-arrow)"/><line x1="188" y1="19" x2="188" y2="121" marker-start="url(#dim-arrow)" marker-end="url(#dim-arrow)"/><text x="81" y="9">FIELD VERIFY</text><text x="191" y="80" transform="rotate(90 191 80)">SNOHOMISH CO.</text></svg>
      {blueprint_svg(slug)}
    </div>"""


def map_pin_stage() -> str:
    return """<div class="blueprint-stage" data-blueprint="map-pin" aria-label="Snohomish County service area map pin drawing">
      <svg class="blueprint-grid" viewBox="0 0 384 336" aria-hidden="true"><defs><pattern id="minor-grid" width="12" height="12" patternUnits="userSpaceOnUse"><path class="grid-minor" d="M12 0H0V12" fill="none"/></pattern><pattern id="major-grid" width="96" height="96" patternUnits="userSpaceOnUse"><rect width="96" height="96" fill="url(#minor-grid)"/><path class="grid-major" d="M96 0H0V96" fill="none"/></pattern></defs><rect width="100%" height="100%" fill="url(#major-grid)"/></svg>
      <svg class="dimension-frame" viewBox="0 0 200 140" aria-hidden="true"><line x1="18" y1="12" x2="182" y2="12"/><line x1="188" y1="19" x2="188" y2="121"/><text x="70" y="9">SERVICE RADIUS</text><text x="191" y="74" transform="rotate(90 191 74)">LOCAL CREW</text></svg>
      <svg class="blueprint-drawing" viewBox="0 0 200 140" role="img" aria-label="Map pin blueprint"><g class="blueprint-stroke"><path class="pin-fill" d="M100 18c-27 0-49 21-49 48 0 35 49 64 49 64s49-29 49-64c0-27-22-48-49-48z"/><circle cx="100" cy="65" r="18"/><path d="M32 116l39-19 31 12 39-18 29 12"/><line class="blueprint-accent" x1="24" y1="132" x2="176" y2="132"/><text class="drawing-label" x="55" y="140">SNOHOMISH COUNTY</text></g></svg>
    </div>"""


def replace_hero(source: str, stage: str, hero_class: str) -> str:
    pattern = re.compile(r'<section\s+class=["\']page-hero["\'][^>]*>\s*<div\s+class=["\']container["\']>([\s\S]*?)</div>\s*</section>', re.I)
    match = pattern.search(source)
    if not match:
        return source
    inner = match.group(1)
    replacement = f'<section class="workshop-hero blueprint-hero {hero_class}"><div class="container hero-layout"><div class="hero-copy">{inner}</div>{stage}</div></section>'
    return source[:match.start()] + replacement + source[match.end():]


def service_card(slug: str, name: str, description: str) -> str:
    return f"""<a href="/services/{slug}.html" class="service-card reveal">
      {blueprint_svg(slug, 'card-blueprint')}
      <h3>{html.escape(name)}</h3><p>{html.escape(description)}</p><span class="learn-more">View service</span>
    </a>"""


def homepage_main() -> str:
    cards = "\n".join(service_card(*service) for service in SERVICES)
    chips = "".join(f'<a class="area-chip reveal" href="/areas/{slug}.html">{name}</a>' for slug, name in AREAS)
    return f"""
  <main>
    <section class="workshop-hero blueprint-hero home-hero">
      <div class="container hero-layout">
        <div class="hero-copy"><span class="eyebrow">Built here. Built to code.</span><h1>ADUs, additions and remodels built to Snohomish County code</h1>
          <p class="hero-promise">Registered, bonded $30,000, insured $1,000,000, and permits handled from application through inspection.</p>
          <div class="hero-buttons"><a href="tel:+14252865639" class="btn btn-primary">Call (425) 286-5639</a><a href="#estimate" class="btn btn-outline">Request an estimate</a></div>
        </div>{blueprint_stage('adu-construction')}
      </div>
    </section>

    <section id="services" class="services-workshop">
      <div class="container"><div class="section-header"><div class="section-label">Our Services</div><h2>Home Remodeling Services in Everett, WA</h2><p>Whether you're dreaming of a new kitchen, updating your bathroom, or adding living space with an ADU, we bring your vision to life with quality craftsmanship and clear communication.</p><p><strong>View All 17 Services</strong><br>Siding, flooring, fencing, painting, outdoor living &amp; more</p></div>
        <div class="services-grid">{cards}</div>
      </div>
    </section>

    <section id="process" class="process-section">
      <div class="container"><span class="eyebrow">From field measure to final</span><h2>One accountable build process</h2>
        <div class="process-rail"><span class="process-track" aria-hidden="true"></span><span class="process-progress" aria-hidden="true"></span>
          <article class="process-step reveal" data-step="01"><h3>Site visit</h3><p>We walk the property, document existing conditions, and measure the work.</p></article>
          <article class="process-step reveal" data-step="02"><h3>Fixed-scope proposal</h3><p>Clear scope and pricing, delivered with the required <a href="/contractor-disclosure.html">state disclosure</a>.</p></article>
          <article class="process-step reveal" data-step="03"><h3>Permits</h3><p>Plans, applications, corrections, and inspection scheduling are handled.</p></article>
          <article class="process-step reveal" data-step="04"><h3>Build</h3><p>Sequenced trades, site protection, progress updates, and documented decisions.</p></article>
          <article class="process-step reveal" data-step="05"><h3>Walkthrough</h3><p>Final quality review, corrections, closeout, and a clean handoff.</p></article>
        </div>
        <div class="section-header mt-3"><h3>Ready to Start Your Remodeling Project?</h3><p>Get a free, no-obligation estimate for your home improvement project. We'll visit your home, discuss your vision, and provide a detailed quote.</p><p><a href="#estimate" class="btn btn-primary">Get Your Free Estimate</a> <a href="tel:+14252865639" class="btn btn-navy">Call (425) 286-5639</a></p></div>
      </div>
    </section>

    <section id="areas" class="build-band"><div class="container"><span class="eyebrow">Service Areas</span><h2>Proudly Serving Snohomish County</h2><p>We provide expert home remodeling services throughout Everett and the surrounding communities.</p><div class="area-chips">{chips}</div></div></section>

    <section id="credentials"><div class="container"><div class="section-header"><div class="section-label">Why NW General Contractor</div><h2>Quality Craftsmanship You Can Count On</h2><p>We treat every home like our own. Here's what sets us apart from other contractors in Snohomish County.</p></div>
      <div class="credentials-grid"><div class="credential-card"><span class="credential-value" data-prefix="$" data-count="30000">$30,000</span><span class="credential-label">Surety bond</span></div><div class="credential-card"><span class="credential-value" data-prefix="$" data-count="1000000">$1,000,000</span><span class="credential-label">General liability insurance</span></div><div class="credential-card"><span class="credential-value">NWSTYSH768DA</span><span class="credential-label">WA contractor registration</span></div></div>
      <div class="feature-grid"><article class="feature-item reveal"><h3>Licensed &amp; Insured</h3><p>Fully licensed with WA Labor &amp; Industries, $1M general liability insurance, and $30,000 surety bond. Your project is protected.</p></article><article class="feature-item reveal"><h3>Transparent Pricing</h3><p>Detailed written estimates with no hidden fees. You know exactly what you're paying for before any work begins.</p></article><article class="feature-item reveal"><h3>Quality Materials</h3><p>We use premium materials from trusted suppliers. No cutting corners. Every detail is built to last in the Pacific Northwest climate.</p></article><article class="feature-item reveal"><h3>Clear Communication</h3><p>Regular project updates, responsive to calls and texts, and a dedicated point of contact throughout your entire project.</p></article></div>
      <div class="testimonials"><div class="section-header"><div class="section-label">Testimonials</div><h2>What Our Customers Say</h2><p>We measure our success by the satisfaction of our homeowners. Here's what they have to say about working with us.</p></div><div class="testimonials-grid">
        <article class="testimonial-card reveal"><div class="testimonial-stars">★★★★★</div><p>"NW General Contractor transformed our outdated kitchen into a modern showpiece. The attention to detail and communication throughout the project was outstanding. Highly recommend!"</p><div class="testimonial-author">Satisfied Homeowner</div><small>Everett, WA</small></article>
        <article class="testimonial-card reveal"><div class="testimonial-stars">★★★★★</div><p>"Professional, reliable, and fair pricing. They completed our bathroom remodel on time and the quality exceeded our expectations. We'll definitely use them again for future projects."</p><div class="testimonial-author">Happy Customer</div><small>Marysville, WA</small></article>
        <article class="testimonial-card reveal"><div class="testimonial-stars">★★★★★</div><p>"From the initial estimate to the final walkthrough, the entire experience was seamless. They treated our home with respect and delivered exactly what was promised. Five stars!"</p><div class="testimonial-author">Delighted Client</div><small>Lake Stevens, WA</small></article>
      </div></div>
    </div></section>

    <section id="guides" class="section-light"><div class="container"><div class="section-header"><div class="section-label">From Our Blog</div><h2>Home Improvement Tips &amp; Guides</h2></div><div class="blog-grid">
      <a href="/blog/kitchen-remodel-cost-everett-wa.html" class="blog-card reveal"><div class="blog-card-meta">February 2026 &middot; 8 min read</div><h3>How Much Does a Kitchen Remodel Cost in Everett, WA?</h3><p>A complete breakdown of kitchen remodel costs in the Everett area, from budget-friendly updates to high-end transformations.</p><span class="learn-more">Read guide</span></a>
      <a href="/blog/adu-regulations-snohomish-county.html" class="blog-card reveal"><div class="blog-card-meta">February 2026 &middot; 10 min read</div><h3>ADU Regulations in Snohomish County: What Homeowners Need to Know</h3><p>New regulations make ADUs easier than ever. Learn about permits, costs, and requirements for building an ADU on your property.</p><span class="learn-more">Read guide</span></a>
      <a href="/blog/how-to-choose-general-contractor-everett.html" class="blog-card reveal"><div class="blog-card-meta">February 2026 &middot; 6 min read</div><h3>How to Choose a General Contractor in Everett, WA</h3><p>10 questions to ask before hiring a contractor. Protect your investment and ensure quality results for your remodeling project.</p><span class="learn-more">Read guide</span></a>
    </div></div></section>

    <section id="estimate" class="estimate-section"><div class="container estimate-shell"><div><span class="eyebrow">Start with the scope</span><h2>Let's Build Something Great Together</h2><p>Your dream home is closer than you think. Contact us today for a free consultation and estimate on your next remodeling project.</p><p><strong>Get Started Today</strong></p><p>Prefer to talk through it? Call <a href="tel:+14252865639">(425) 286-5639</a>.</p></div>
      <form class="contact-form estimate-form" novalidate><div class="form-row"><div class="form-group"><label for="home-name">Your name *</label><input id="home-name" name="name" type="text" autocomplete="name" required></div><div class="form-group"><label for="home-phone">Phone</label><input id="home-phone" name="phone" type="tel" autocomplete="tel"></div></div><div class="form-row"><div class="form-group"><label for="home-email">Email *</label><input id="home-email" name="email" type="email" autocomplete="email" required></div><div class="form-group"><label for="home-city">City</label><input id="home-city" name="city" type="text" autocomplete="address-level2"></div></div><div class="form-group"><label for="home-service">Project type</label><select id="home-service" name="service"><option value="">Select a service</option><option value="adu">ADU Construction</option><option value="addition">Home Addition</option><option value="kitchen">Kitchen Remodeling</option><option value="bathroom">Bathroom Remodeling</option><option value="whole-home">Whole Home Renovation</option><option value="deck">Deck Building</option><option value="other">Other</option></select></div><div class="form-group"><label for="home-message">Project details *</label><textarea id="home-message" name="message" required></textarea></div><button class="btn btn-primary" type="submit">Request an estimate</button></form>
    </div></section>
  </main>"""


def page_kind(rel: str) -> tuple[str, str]:
    if rel == "index.html": return "home", ""
    if rel.startswith("services/"): return "service", "services"
    if rel.startswith("areas/"): return "area", "areas"
    if rel.startswith("blog/"): return "blog", "blog"
    if rel == "portfolio.html": return "portfolio", "portfolio"
    if rel == "contact.html": return "contact", "contact"
    return "utility", ""


def replace_header_block(source: str, replacement: str) -> tuple[str, int]:
    """Replace legacy chrome whether or not a page had the optional top bar."""
    header_match = re.search(r'<header\b[\s\S]*?</header>', source, flags=re.I)
    if not header_match:
        return source, 0
    start = header_match.start()
    top_bars = list(re.finditer(r'<div\s+class=["\']top-bar["\']', source[:start], flags=re.I))
    if top_bars:
        start = top_bars[-1].start()
    prefix = source[:start].rstrip(" \t\r\n")
    suffix = source[header_match.end():].lstrip(" \t\r\n")
    return prefix + "\n" + replacement.strip() + "\n" + suffix, 1


def migrate_page(path: Path) -> None:
    rel = path.relative_to(ROOT).as_posix()
    kind, active = page_kind(rel)
    source = path.read_text(encoding="utf-8")
    if "workshop-page" in source:
        source = ensure_favicon(source)
        source, header_count = replace_header_block(source, header(active))
        if header_count != 1:
            raise RuntimeError(f"{rel}: could not refresh header")
        source, footer_count = re.subn(r'<footer\b[\s\S]*?</footer>', footer().strip(), source, count=1, flags=re.I)
        if footer_count != 1:
            raise RuntimeError(f"{rel}: could not refresh footer")
        source = normalize_footer_spacing(source)
        if source != path.read_text(encoding="utf-8"):
            path.write_text(source, encoding="utf-8", newline="\n")
            print(f"refreshed {rel}")
        else:
            print(f"skip {rel}: already current")
        return

    source = ensure_favicon(source)
    if not has_valid_contractor(source):
        source = source.replace("</head>", GENERAL_CONTRACTOR + "</head>", 1)

    source, count = replace_header_block(source, header(active))
    if count != 1:
        raise RuntimeError(f"{rel}: could not replace header")

    source = re.sub(r'<body(?:\s+class=["\'][^"\']*["\'])?\s*>', f'<body class="workshop-page page-{kind}">', source, count=1, flags=re.I)

    if kind == "home":
        head_end = source.index("</header>") + len("</header>")
        footer_start = source.index("<footer", head_end)
        source = source[:head_end] + "\n" + homepage_main() + "\n" + source[footer_start:]
    elif kind == "service":
        slug = path.stem
        source = replace_hero(source, blueprint_stage(slug), "service-hero")
        source = source.replace('class="content-wrapper"', 'class="content-wrapper service-layout"', 1)
        source = source.replace('class="sidebar"', 'class="sidebar sticky-estimate"', 1)
        faq_pattern = re.compile(r'<div\s+class=["\']faq-item["\']>\s*<button\s+class=["\']faq-question["\']>([\s\S]*?)</button>\s*<div\s+class=["\']faq-answer["\']>\s*<div\s+class=["\']faq-answer-inner["\']>([\s\S]*?)</div>\s*</div>\s*</div>', re.I)
        source = faq_pattern.sub(lambda m: f'<details class="faq-item"><summary class="faq-question">{m.group(1)}</summary><div class="faq-answer"><div class="faq-answer-inner">{m.group(2)}</div></div></details>', source)
    elif kind == "area":
        source = replace_hero(source, map_pin_stage(), "area-hero")
        source = source.replace('class="content-wrapper"', 'class="content-wrapper area-layout"', 1)
        source = source.replace('class="sidebar"', 'class="sidebar sticky-estimate"', 1)
    else:
        source = replace_hero(source, blueprint_stage("whole-home-renovation"), "workshop-subhero")

    if rel == "contact.html":
        source = source.replace('<section class="content-section">', '<section class="content-section" id="estimate">', 1)
    if rel == "about.html":
        source = re.sub(r'<img\s+src=["\']images/david-headshot\.jpg["\']([^>]*)>', r'<img src="images/david-headshot.jpg" width="600" height="750" loading="lazy"\1>', source, count=1, flags=re.I)

    if rel == "portfolio.html":
        source = source.replace('<div class="portfolio-grid">', '<p class="portfolio-notice">Real job photos are being added; call for references</p>\n      <div class="portfolio-grid">', 1)
        tile_slugs = ["kitchen-remodeling", "bathroom-remodeling", "adu-construction", "deck-building", "home-additions", "whole-home-renovation"]
        for slug in tile_slugs:
            source, replaced = re.subn(r'(<div\s+class=["\']portfolio-item["\']>\s*<div>)\s*<svg[\s\S]*?</svg>', lambda m, slug=slug: m.group(1) + blueprint_svg(slug, "portfolio-blueprint"), source, count=1, flags=re.I)
            if replaced != 1:
                raise RuntimeError(f"{rel}: portfolio tile replacement failed for {slug}")

    for class_name in ("service-card", "feature-item", "testimonial-card", "blog-card", "portfolio-item"):
        source = re.sub(rf'class=["\']{class_name}["\']', f'class="{class_name} reveal"', source)

    source, footer_count = re.subn(r'<footer\b[\s\S]*?</footer>', footer().strip(), source, count=1, flags=re.I)
    if footer_count != 1:
        raise RuntimeError(f"{rel}: could not replace footer")
    source = normalize_footer_spacing(source)
    source = re.sub(r'\s*<!--\s*Mobile sticky CTA bar\s*-->\s*<div\s+class=["\']mobile-bottom-cta["\'][\s\S]*?</div>', "", source, flags=re.I)
    source = re.sub(r'\s*<script\s+src=["\'][^"\']*/?js/(?:tracking|main|glow|ui)\.js["\']\s*></script>', "", source, flags=re.I)
    scripts = '<script src="/js/tracking.js"></script>\n  '
    if rel == "index.html":
        scripts += '<script src="/js/glow.js"></script>\n  '
    scripts += '<script src="/js/main.js"></script>\n  <script src="/js/ui.js"></script>'
    source = source.replace("</body>", mobile_bar(kind == "home") + "\n  " + scripts + "\n</body>", 1)
    path.write_text(source, encoding="utf-8", newline="\n")
    print(f"migrated {rel}")


def main() -> None:
    pages = sorted(ROOT.rglob("*.html"), key=lambda path: path.as_posix())
    if len(pages) != 48:
        raise RuntimeError(f"expected 48 HTML pages, found {len(pages)}")
    for page in pages:
        migrate_page(page)
    print(f"Workshop migration complete: {len(pages)} pages")


if __name__ == "__main__":
    main()

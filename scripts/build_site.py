#!/usr/bin/env python3
"""Apply the approved Workshop homepage structure and stamp local assets."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from tools.workshop_migrate import blueprint_stage, blueprint_svg  # noqa: E402


FONT_PRELOADS = (
    "/assets/fonts/barlow-condensed-800.woff2",
    "/assets/fonts/ibm-plex-sans-var.woff2",
)


def hash8(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def stamped(root_url: str) -> str:
    path = ROOT.joinpath(*root_url.lstrip("/").split("/"))
    if not path.is_file():
        raise FileNotFoundError(f"asset URL does not resolve: {root_url}")
    return f"{root_url}?v={hash8(path)}"


def homepage_hero() -> str:
    drawing = blueprint_stage("adu-construction").replace(
        "DETACHED ADU / SITE 01", "DETACHED ADU / PLAN"
    )
    return f'''<section class="workshop-hero blueprint-hero home-hero">
      <div class="container hero-layout">
        <div class="hero-copy">
          <h1><span class="hero-title-line">ADUs, additions and remodels built</span> <span class="hero-title-line">to Snohomish County code</span></h1>
          <p class="hero-promise">Registered, bonded, insured, and organized from permit application through final inspection.</p>
          <div class="hero-proof" aria-label="Contractor credentials">
            <div class="hero-proof__item"><strong>NWSTYSH768DA</strong>WA registration</div>
            <div class="hero-proof__item"><strong>$30,000</strong>Surety bond</div>
            <div class="hero-proof__item"><strong>$1,000,000</strong>General liability</div>
            <div class="hero-proof__item"><strong>Application to inspection</strong>Permits handled</div>
          </div>
          <div class="hero-identity">
            <img class="hero-identity__portrait" src="/images/david-headshot.jpg" width="600" height="750" alt="David, owner and general contractor" decoding="async" fetchpriority="high">
            <div><span class="hero-identity__name">David</span><span class="hero-identity__role">Owner and General Contractor</span><span class="hero-identity__registration">WA registration NWSTYSH768DA</span></div>
            <a class="hero-identity__phone" href="tel:+14254397700">(425) 439-7700</a>
          </div>
          <div class="hero-buttons"><a class="btn btn-primary" href="tel:+14254397700">Call (425) 439-7700</a><a class="btn btn-outline" href="#estimate">Request an estimate</a></div>
        </div>
        {drawing}
      </div>
    </section>'''


def process_section() -> str:
    return '''<section id="process" class="process-section">
      <div class="container">
        <span class="eyebrow">Field measure to final</span>
        <h2>One accountable build process</h2>
        <div class="process-rail"><span class="process-track" aria-hidden="true"></span><span class="process-progress" aria-hidden="true"></span>
          <article class="process-step reveal"><span class="process-step__label">Site visit</span><h3>Measure the work</h3><p>We walk the property, document existing conditions, and measure the work.</p></article>
          <article class="process-step reveal"><span class="process-step__label">Proposal</span><h3>Fix the scope</h3><p>Clear scope and pricing, delivered with the required <a href="/contractor-disclosure.html">state disclosure</a>.</p></article>
          <article class="process-step reveal"><span class="process-step__label">Permits</span><h3>Submit and respond</h3><p>Plans, applications, corrections, and inspection scheduling are handled.</p></article>
          <article class="process-step reveal"><span class="process-step__label">Build</span><h3>Sequence the trades</h3><p>Sequenced trades, site protection, progress updates, and documented decisions.</p></article>
          <article class="process-step reveal"><span class="process-step__label">Walkthrough</span><h3>Close the project</h3><p>Final quality review, corrections, closeout, and a clean handoff.</p></article>
        </div>
      </div>
    </section>'''


def credentials_section() -> str:
    return '''<section id="credentials" class="credentials-section"><div class="container">
      <div class="section-header"><h2>Credentials you can verify</h2><p>Registration, bond, coverage, and permit responsibility stated plainly.</p></div>
      <div class="credentials-grid">
        <div class="credential-card"><span class="credential-value">NWSTYSH768DA</span><span class="credential-label">Washington contractor registration</span></div>
        <div class="credential-card"><span class="credential-value">$30,000</span><span class="credential-label">Surety bond</span></div>
        <div class="credential-card"><span class="credential-value">$1,000,000</span><span class="credential-label">General liability insurance</span></div>
        <div class="credential-card"><span class="credential-value">Permits handled</span><span class="credential-label">Application through inspection<br><a href="/contractor-disclosure.html">Read the state disclosure</a></span></div>
      </div>
    </div></section>'''


def estimate_section() -> str:
    return '''<section id="estimate" class="estimate-section"><div class="container estimate-shell"><div><h2>Start with a clear scope</h2><p>Tell us what must change, where the property is, and what you need priced. We will identify the next useful step.</p><p><strong>Prefer to talk through it?</strong> Call <a href="tel:+14254397700">(425) 439-7700</a>.</p><p>Before comparing proposals, <a href="/about.html#project-planning">prepare your Everett and Snohomish County planning worksheet</a>.</p></div>
      <form class="contact-form estimate-form" novalidate><div class="form-row"><div class="form-group"><label for="home-name">Your name *</label><input id="home-name" name="name" type="text" autocomplete="name" required></div><div class="form-group"><label for="home-phone">Phone</label><input id="home-phone" name="phone" type="tel" autocomplete="tel"></div></div><div class="form-row"><div class="form-group"><label for="home-email">Email *</label><input id="home-email" name="email" type="email" autocomplete="email" required></div><div class="form-group"><label for="home-city">City</label><input id="home-city" name="city" type="text" autocomplete="address-level2"></div></div><div class="form-group"><label for="home-service">Project type</label><select id="home-service" name="service"><option value="">Select a service</option><option value="adu">ADU Construction</option><option value="addition">Home Addition</option><option value="kitchen">Kitchen Remodeling</option><option value="bathroom">Bathroom Remodeling</option><option value="whole-home">Whole Home Renovation</option><option value="deck">Deck Building</option><option value="other">Other</option></select></div><div class="form-group"><label for="home-message">Project details *</label><textarea id="home-message" name="message" required></textarea></div><button class="btn btn-primary" type="submit">Request an estimate</button></form>
    </div></section>'''


def rewrite_homepage(source: str) -> str:
    if "nwgc-cover" in source:
        source, count = re.subn(
            r'<section class="workshop-hero blueprint-hero home-hero nwgc-cover">[\s\S]*?</section>',
            homepage_hero(),
            source,
            count=1,
        )
        if count != 1:
            raise RuntimeError("homepage hero replacement failed")

    card_pattern = re.compile(
        r'<a href="([^"]+)" class="service-card reveal">\s*(<svg[\s\S]*?</svg>)\s*'
        r'<h3>([\s\S]*?)</h3><p>([\s\S]*?)</p><span class="learn-more">[\s\S]*?</span>\s*</a>'
    )
    cards = list(card_pattern.finditer(source))
    if cards:
        if len(cards) != 17:
            raise RuntimeError(f"expected 17 homepage service cards, found {len(cards)}")
        counter = iter(range(1, 18))

        def ledger_row(match: re.Match[str]) -> str:
            sheet = next(counter)
            drawing = match.group(2).replace('class="card-blueprint"', 'class="service-ledger__drawing"')
            return (
                f'<a href="{match.group(1)}" class="service-ledger__row reveal">\n'
                f'      {drawing}\n'
                f'      <div class="service-ledger__copy"><span class="service-ledger__sheet">A-{sheet:02d}</span>'
                f'<h3>{match.group(3)}</h3><p>{match.group(4)}</p></div>\n    </a>'
            )

        source = card_pattern.sub(ledger_row, source)
        source = source.replace(
            '<div class="container"><div class="section-header"><div class="section-label">Our Services</div><h2>Home Remodeling Services in Everett, WA</h2><p>Whether you\'re dreaming of a new kitchen, updating your bathroom, or adding living space with an ADU, we bring your vision to life with quality craftsmanship and clear communication.</p><p><strong>View All 17 Services</strong><br>Siding, flooring, fencing, painting, outdoor living &amp; more</p></div>\n        <div class="services-grid">',
            '<div class="container"><div class="section-header"><h2>What we build</h2><p>Seventeen scopes for Snohomish County homes, indexed like a drawing set. Start with the work you need priced.</p></div>\n        <div class="service-ledger">',
            1,
        )

    source = re.sub(
        r'<section id="process" class="process-section">[\s\S]*?</section>',
        process_section(), source, count=1,
    )
    source = source.replace(
        '<section id="areas" class="build-band"><div class="container"><span class="eyebrow">Service Areas</span>',
        '<section id="areas" class="build-band"><div class="container">',
        1,
    )
    source = re.sub(
        r'<section id="credentials">[\s\S]*?</section>',
        credentials_section(), source, count=1,
    )
    source = source.replace(
        '<div class="section-header"><div class="section-label">From Our Blog</div><h2>Home Improvement Tips &amp; Guides</h2></div>',
        '<div class="section-header"><span class="eyebrow">Recent guides</span><h2>Permits, costs, and contractor checks</h2></div>',
        1,
    )
    source = re.sub(
        r'<section id="estimate" class="estimate-section">[\s\S]*?</section>',
        estimate_section(), source, count=1,
    )
    source = re.sub(
        r'\s*<section class="content-section"><div class="container"><h2>Prepare a clearer remodeling brief</h2>[\s\S]*?</section>(?=<footer>)',
        "",
        source,
        count=1,
    )
    source = re.sub(r'\s*<script src="/js/glow\.js(?:\?v=[0-9a-f]+)?"></script>', "", source)
    return source


def rewrite_about(source: str) -> str:
    source = source.replace(
        '<div style="float:right;margin:0 0 1.5rem 2rem;text-align:center;max-width:280px;">\n'
        '            <img src="images/david-headshot.jpg" width="600" height="750" loading="lazy" alt="David - Owner of NW General Contractor" style="width:100%;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.12);">\n'
        '            <p style="font-size:0.85rem;color:var(--gray-600);margin-top:0.75rem;font-weight:600;">David &mdash; Owner &amp; General Contractor</p>\n'
        '          </div>',
        '<figure class="about-portrait">\n'
        '            <img src="/images/david-headshot.jpg" width="600" height="750" loading="lazy" alt="David - Owner of NW General Contractor">\n'
        '            <figcaption>David &mdash; Owner &amp; General Contractor</figcaption>\n'
        '          </figure>',
        1,
    )
    return source


def rewrite_portfolio(source: str) -> str:
    tile_drawings = {
        "Kitchen Remodel": "kitchen-remodeling",
        "Bathroom Renovation": "bathroom-remodeling",
        "ADU Construction": "adu-construction",
        "Deck &amp; Outdoor Living": "deck-building",
        "Home Addition": "home-additions",
        "Whole Home Renovation": "whole-home-renovation",
    }
    for title, slug in tile_drawings.items():
        pattern = re.compile(
            r'(<div class="portfolio-item reveal">\s*<div>)([\s\S]*?)'
            + re.escape(title)
            + r'(<br><small>Coming Soon</small></p>\s*</div>\s*</div>)'
        )
        match = pattern.search(source)
        if not match:
            raise RuntimeError(f"portfolio tile not found: {title}")
        prefix = match.group(1)
        middle = re.sub(r'<svg[\s\S]*?</svg>', blueprint_svg(slug, "portfolio-blueprint"), match.group(2), count=1)
        source = source[:match.start()] + prefix + middle + title + match.group(3) + source[match.end():]
    return source


def normalize_head(source: str) -> str:
    source = re.sub(r'\s*<link\b[^>]*href=["\'][^"\']*(?:css/identity\.css|assets/identity/motion\.css)[^"\']*["\'][^>]*>', "", source, flags=re.I)
    source = re.sub(r'\s*<script\b[^>]*src=["\'][^"\']*assets/identity/motion\.js[^"\']*["\'][^>]*></script>', "", source, flags=re.I)
    source = re.sub(r'\s*<link\b[^>]*rel=["\']preload["\'][^>]*href=["\'][^"\']*/assets/fonts/[^"\']+["\'][^>]*>', "", source, flags=re.I)
    for property_name in ("og:image", "og:image:width", "og:image:height", "og:image:alt"):
        source = re.sub(rf'\s*<meta\b[^>]*property=["\']{re.escape(property_name)}["\'][^>]*>', "", source, flags=re.I)
    for name in ("twitter:card", "twitter:image"):
        source = re.sub(rf'\s*<meta\b[^>]*name=["\']{re.escape(name)}["\'][^>]*>', "", source, flags=re.I)

    style_url = stamped("/css/style.css")
    source, count = re.subn(
        r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*href=["\'][^"\']*css/style\.css(?:\?[^"\']*)?["\'][^>]*>',
        f'<link rel="stylesheet" href="{style_url}">',
        source,
        count=1,
        flags=re.I,
    )
    if count != 1:
        raise RuntimeError("style link normalization failed")

    preload_markup = "\n".join(
        f'<link rel="preload" href="{stamped(url)}" as="font" type="font/woff2" crossorigin>'
        for url in FONT_PRELOADS
    )
    social_url = stamped("/assets/og.png")
    social_markup = (
        f'<meta property="og:image" content="https://nwgeneralcontractor.com{social_url}">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:alt" content="NW General Contractor Workshop blueprint drawing">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="https://nwgeneralcontractor.com{social_url}">'
    )
    source = source.replace(f'<link rel="stylesheet" href="{style_url}">', f'{preload_markup}\n  <link rel="stylesheet" href="{style_url}">', 1)
    source = source.replace("</head>", f"  {social_markup}\n</head>", 1)
    return source


def stamp_html_assets(source: str) -> str:
    def replace_script(match: re.Match[str]) -> str:
        raw = match.group(1)
        path = urlsplit(raw).path
        if not path.startswith("/js/"):
            return match.group(0)
        return match.group(0).replace(raw, stamped(path))

    source = re.sub(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', replace_script, source, flags=re.I)

    def replace_image(match: re.Match[str]) -> str:
        raw = match.group(1)
        path = urlsplit(raw).path
        if not path.startswith("/"):
            path = "/" + path.lstrip("./")
        target = ROOT.joinpath(*path.lstrip("/").split("/"))
        if not target.is_file():
            return match.group(0)
        return match.group(0).replace(raw, stamped(path))

    return re.sub(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', replace_image, source, flags=re.I)


def stamp_font_urls() -> None:
    css_path = ROOT / "css" / "style.css"
    source = css_path.read_text(encoding="utf-8")

    def replace_font(match: re.Match[str]) -> str:
        return f"url('{stamped(match.group(1))}')"

    source = re.sub(
        r"url\([\"']?(/assets/fonts/[^?\"')]+)(?:\?v=[0-9a-f]+)?[\"']?\)",
        replace_font,
        source,
    )
    css_path.write_text(source, encoding="utf-8", newline="\n")


def main() -> None:
    stamp_font_urls()
    pages = sorted(
        [
            *ROOT.glob("*.html"),
            *ROOT.glob("areas/*.html"),
            *ROOT.glob("blog/*.html"),
            *ROOT.glob("services/*.html"),
        ],
        key=lambda path: path.as_posix(),
    )
    if len(pages) != 48:
        raise RuntimeError(f"expected 48 HTML pages, found {len(pages)}")
    for page in pages:
        source = page.read_text(encoding="utf-8")
        if page == ROOT / "index.html":
            source = rewrite_homepage(source)
        elif page == ROOT / "about.html":
            source = rewrite_about(source)
        elif page == ROOT / "portfolio.html":
            source = rewrite_portfolio(source)
        source = normalize_head(source)
        source = stamp_html_assets(source)
        page.write_text(source, encoding="utf-8", newline="\n")
    print(f"Workshop build complete: stamped {len(pages)} pages")


if __name__ == "__main__":
    main()

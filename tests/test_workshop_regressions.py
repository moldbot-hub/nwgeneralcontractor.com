import hashlib
import re
import struct
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
HTML_PAGES = sorted(
    [
        *ROOT.glob("*.html"),
        *ROOT.glob("areas/*.html"),
        *ROOT.glob("blog/*.html"),
        *ROOT.glob("services/*.html"),
    ]
)
PHONE_COUNTS = {
    "404.html": (4, 6), "about.html": (6, 8),
    "areas/arlington.html": (5, 7), "areas/bothell.html": (5, 7),
    "areas/everett.html": (4, 6), "areas/lake-stevens.html": (5, 7),
    "areas/lynnwood.html": (5, 7), "areas/marysville.html": (5, 7),
    "areas/mill-creek.html": (5, 7), "areas/mukilteo.html": (5, 7),
    "areas/snohomish.html": (5, 7),
    "blog/adu-cost-snohomish-county.html": (5, 7),
    "blog/adu-regulations-snohomish-county.html": (5, 7),
    "blog/bathroom-remodel-cost-everett-wa.html": (4, 6),
    "blog/deck-cost-guide-everett.html": (7, 7),
    "blog/deck-materials-washington.html": (5, 7),
    "blog/home-addition-cost-everett.html": (5, 7),
    "blog/how-long-kitchen-remodel.html": (4, 6),
    "blog/how-to-choose-general-contractor-everett.html": (5, 7),
    "blog/index.html": (4, 6), "blog/kitchen-remodel-cost-everett-wa.html": (5, 7),
    "blog/remodel-permit-snohomish-county.html": (4, 6),
    "blog/roofing-cost-snohomish-county.html": (4, 6),
    "blog/siding-cost-guide-everett.html": (7, 7),
    "blog/siding-replacement-everett-wa.html": (4, 6),
    "blog/whole-home-renovation-cost-everett.html": (5, 7),
    "contact.html": (6, 6), "contractor-disclosure.html": (5, 7),
    "index.html": (7, 8), "portfolio.html": (4, 6), "privacy.html": (5, 6),
    "services/adu-construction.html": (5, 7),
    "services/bathroom-remodeling.html": (5, 7),
    "services/custom-carpentry.html": (5, 7),
    "services/deck-building.html": (5, 7), "services/fencing.html": (5, 7),
    "services/flooring.html": (5, 7), "services/foundation-repair.html": (5, 7),
    "services/garage-construction.html": (5, 7),
    "services/home-additions.html": (5, 7),
    "services/kitchen-remodeling.html": (5, 7),
    "services/outdoor-living.html": (5, 7), "services/painting.html": (5, 7),
    "services/patio-concrete.html": (5, 7), "services/roofing.html": (5, 7),
    "services/siding.html": (5, 7),
    "services/whole-home-renovation.html": (5, 7),
    "services/windows-doors.html": (5, 7),
}


def block_after(source: str, marker: str) -> str:
    """Return the balanced CSS block that begins at marker."""
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[opening + 1:index]
    raise AssertionError(f"unclosed CSS block after {marker}")


def css_rule(source: str, selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", source)
    if not match:
        raise AssertionError(f"missing CSS rule for {selector}")
    return match.group(1).replace(" ", "")


def luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class WorkshopRegressionTests(unittest.TestCase):
    def test_shared_header_logo_has_real_transparency(self):
        logo = Image.open(ROOT / "images" / "logo-sm.png")
        master = Image.open(ROOT / "images" / "logo.png").convert("RGBA")
        self.assertEqual("RGBA", logo.mode)
        self.assertEqual(master.size, logo.size)
        corners = [
            logo.getpixel(point)[3]
            for point in (
                (0, 0),
                (logo.width - 1, 0),
                (0, logo.height - 1),
                (logo.width - 1, logo.height - 1),
            )
        ]
        self.assertEqual([0, 0, 0, 0], corners)
        self.assertGreater(max(pixel[3] for pixel in logo.get_flattened_data()), 240)
        alpha = bytes(pixel[3] for pixel in logo.get_flattened_data())
        self.assertEqual(69_469, sum(value > 0 for value in alpha))
        self.assertEqual(
            "9cbfa0d24f284c9422ce1212df58494b97600ded7b000d9c620e2f150df2b910",
            hashlib.sha256(alpha).hexdigest(),
        )
        changed_visible_pixels = [
            index
            for index, (source, output) in enumerate(
                zip(master.get_flattened_data(), logo.get_flattened_data())
            )
            if output[3] and source[:3] != output[:3]
        ]
        self.assertEqual([], changed_visible_pixels[:1])

        self.assertEqual(48, len(HTML_PAGES))
        for page in HTML_PAGES:
            self.assertIn(
                'src="/images/logo-sm.png?v=',
                page.read_text(encoding="utf-8"),
                page,
            )

    def test_workshop_fonts_are_local_and_applied(self):
        expected_fonts = {
            "barlow-condensed-700.woff2",
            "barlow-condensed-800.woff2",
            "ibm-plex-sans-var.woff2",
            "ibm-plex-mono-400.woff2",
            "ibm-plex-mono-500.woff2",
        }
        self.assertEqual(expected_fonts, {path.name for path in (ROOT / "assets" / "fonts").glob("*.woff2")})
        compact = re.sub(r"\s+", "", CSS).lower()
        self.assertEqual(5, compact.count("@font-face"))
        self.assertIn("font-family:'barlowcondensed'", compact)
        self.assertIn("font-family:'ibmplexsans'", compact)
        self.assertIn("font-family:'ibmplexmono'", compact)
        self.assertIn("font-display:swap", compact)
        self.assertIn("unicode-range:", compact)
        for css_file in (ROOT / "css").rglob("*.css"):
            source = css_file.read_text(encoding="utf-8").lower()
            self.assertNotIn("georgia", source, css_file)
            self.assertIsNone(re.search(r"(?<!sans-)\bserif\b", source), css_file)

    def test_exact_workshop_tokens_and_no_gradients_or_glow(self):
        compact = re.sub(r"\s+", "", CSS).lower()
        for token in (
            "--charcoal:#161616", "--concrete:#e7e4dc", "--paper:#fbfaf7",
            "--ink:#1c1c1c", "--steel:#586873", "--steel-light:#b8c1c5",
            "--orange:#ff6a13", "--orange-text:#a94000", "--bone:#f4f1ea",
        ):
            self.assertIn(token, compact)
        self.assertNotIn("gradient", compact)
        self.assertNotIn("glow", compact)

    def test_retired_identity_layer_is_absent(self):
        self.assertFalse((ROOT / "css" / "identity.css").exists())
        self.assertFalse((ROOT / "assets" / "identity").exists())
        for path in (*HTML_PAGES, *(ROOT / "css").rglob("*.css"), *(ROOT / "js").rglob("*.js")):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("/assets/identity", source, path)
            self.assertNotIn("css/identity", source, path)

    def test_every_page_has_hashed_styles_scripts_and_font_preloads(self):
        required_preloads = {
            "/assets/fonts/barlow-condensed-800.woff2",
            "/assets/fonts/ibm-plex-sans-var.woff2",
        }
        for page in HTML_PAGES:
            source = page.read_text(encoding="utf-8")
            found_preloads = set()
            for match in re.finditer(r'<link\b([^>]+)>', source, re.I):
                attrs = dict(re.findall(r'([\w-]+)=["\']([^"\']*)', match.group(1)))
                if attrs.get("rel") == "preload" and attrs.get("as") == "font":
                    found_preloads.add(attrs["href"].split("?", 1)[0])
                    self._assert_hashed_asset(attrs["href"], page)
                if attrs.get("rel") == "stylesheet":
                    self._assert_hashed_asset(attrs["href"], page)
            self.assertEqual(required_preloads, found_preloads, page)
            for src in re.findall(r'<script\b[^>]*\bsrc=["\']([^"\']+)', source, re.I):
                self._assert_hashed_asset(src, page)

    def _assert_hashed_asset(self, url, page):
        match = re.fullmatch(r"(/[^?]+)\?v=([0-9a-f]{8})", url)
        self.assertIsNotNone(match, (page, url))
        asset = ROOT.joinpath(*match.group(1).lstrip("/").split("/"))
        self.assertTrue(asset.is_file(), (page, url))
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:8]
        self.assertEqual(digest, match.group(2), (page, url))

    def test_phone_occurrence_counts_are_unchanged_on_every_page(self):
        self.assertEqual(48, len(PHONE_COUNTS))
        for page in HTML_PAGES:
            rel = page.relative_to(ROOT).as_posix()
            source = page.read_text(encoding="utf-8")
            self.assertEqual(PHONE_COUNTS[rel][0], source.count("(425) 548-1993"), rel)
            self.assertEqual(PHONE_COUNTS[rel][1], source.count("+14255481993"), rel)

    def test_homepage_is_a_ledger_with_plain_visible_copy(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(17, len(re.findall(r'class=["\'][^"\']*\bservice-ledger__row\b', source)))
        self.assertIn('class="hero-identity"', source)
        self.assertNotIn('class="testimonials"', source)
        self.assertNotIn("data-count", source)
        visible = re.sub(r"<(script|style|svg)\b[\s\S]*?</\1>", " ", source, flags=re.I)
        visible = re.sub(r"<[^>]+>", " ", visible)
        visible = re.sub(r"\s+", " ", visible).lower()
        self.assertNotIn("â€”", visible)
        for word in ("transform", "seamless", "dream", "elevate", "hassle-free", "unleash", "next-gen"):
            self.assertIsNone(re.search(rf"\b{re.escape(word)}\b", visible), word)
        self.assertNotIn("!", visible)

    def test_round_two_homepage_layout_contract(self):
        hero = css_rule(CSS, ".home-hero")
        self.assertIn("padding:clamp(48px,7vw,88px)0", hero)
        layout = css_rule(CSS, ".home-hero .hero-layout")
        self.assertIn("row-gap:0", layout)
        self.assertIn("min-height:0", layout)
        promise = css_rule(CSS, ".hero-promise")
        self.assertIn("margin-top:20px!important", promise)
        self.assertIn("margin-bottom:0", promise)
        self.assertIn("margin-top:40px", css_rule(CSS, ".hero-proof"))
        self.assertIn("margin-top:32px", css_rule(CSS, ".hero-identity"))
        self.assertIn("margin-top:32px", css_rule(CSS, ".hero-buttons"))
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(2, source.count('class="hero-title-line"'))
        desktop = re.sub(r"\s+", "", block_after(CSS, "@media (min-width:900px)"))
        self.assertIn(".home-hero.blueprint-stage{grid-column:2;grid-row:1/6;align-self:center}", desktop)
        self.assertIn(".hero-title-line{display:block}", desktop)
        phone = re.sub(r"\s+", "", block_after(CSS, "@media (max-width:720px)"))
        self.assertIn(".hero-title-line{display:inline}", phone)

    def test_round_two_recent_guides_are_asymmetric_only_on_homepage(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<section id="guides" class="section-light recent-guides">', source)
        guides = css_rule(CSS, ".recent-guides .blog-grid")
        self.assertIn("grid-template-columns:minmax(0,2fr)minmax(300px,1fr)", guides)
        self.assertIn("grid-template-rows:repeat(2,1fr)", guides)
        featured = css_rule(CSS, ".recent-guides .blog-card:first-child")
        self.assertIn("grid-row:1/3", featured)
        self.assertIn("min-height:0", css_rule(CSS, ".recent-guides .blog-card:not(:first-child)"))
        phone = re.sub(r"\s+", "", block_after(CSS, "@media (max-width:720px)"))
        self.assertIn(".recent-guides.blog-grid{grid-template-columns:1fr;grid-template-rows:none}", phone)

    def test_round_two_service_ledger_uses_fixed_tracks_and_text_minimum(self):
        self.assertIn("grid-auto-rows:166px", css_rule(CSS, ".service-ledger"))
        row = css_rule(CSS, ".service-ledger__row")
        self.assertIn("grid-template-columns:132pxminmax(180px,1fr)", row)
        self.assertIn("min-height:0", row)
        drawing = css_rule(CSS, ".service-ledger__drawing")
        self.assertIn("width:112px", drawing)
        self.assertIn("height:96px", drawing)
        self.assertIn("min-width:180px", css_rule(CSS, ".service-ledger__copy"))
        phone = re.sub(r"\s+", "", block_after(CSS, "@media (max-width:720px)"))
        self.assertIn(".service-ledger{grid-auto-rows:142px}", phone)
        self.assertIn("grid-template-columns:96pxminmax(184px,1fr)", phone)

    def test_sub_900_layout_is_static_and_has_no_reserved_height(self):
        mobile = block_after(CSS, "@media (max-width:900px)")
        compact = re.sub(r"\s+", "", mobile)
        self.assertIn("section{height:auto!important;min-height:0!important;max-height:none!important}", compact)
        self.assertIn(".sticky-estimate{position:static!important;top:auto!important}", compact)
        self.assertIn("grid-template-columns:1fr", compact)
        self.assertIn(".blueprint-stage{height:auto!important;min-height:0!important;max-height:none!important", compact)
        self.assertIn(".reveal{opacity:1!important;transform:none!important}", compact)

    def test_mobile_parallax_is_disabled(self):
        ui = (ROOT / "js" / "ui.js").read_text(encoding="utf-8")
        self.assertIn("matchMedia('(max-width: 899px)')", ui)
        self.assertRegex(ui, r"if \(reduced\.matches \|\| mobileLayout\.matches\) return;")

    def test_wordmark_and_tagline_are_separate_lines(self):
        self.assertIn("display:block", css_rule(CSS, ".logo-text"))
        tagline = css_rule(CSS, ".logo-tagline")
        self.assertIn("display:block", tagline)
        self.assertRegex(tagline, r"margin-top:\.\d+rem")
        below_1100 = re.sub(r"\s+", "", block_after(CSS, "@media (max-width:1100px)"))
        self.assertIn(".logo-tagline{display:none}", below_1100)

    def test_blueprint_captions_are_plain_filled_text(self):
        label = css_rule(CSS, ".drawing-label")
        self.assertIn("stroke:none!important", label)
        self.assertIn("paint-order:normal", label)
        self.assertRegex(label, r"font:(?:[^;]*\s)?(?:8|9|10)pxvar\(--mono\)")

    def test_text_accent_passes_wcag_aa_on_light_grounds(self):
        match = re.search(r"--orange-text:(#[0-9a-fA-F]{6})", CSS)
        self.assertIsNotNone(match)
        text_accent = match.group(1)
        self.assertGreaterEqual(contrast(text_accent, "#e9e6df"), 4.5)
        self.assertGreaterEqual(contrast(text_accent, "#fbfaf7"), 4.5)
        labels = css_rule(CSS, ".section-label,.eyebrow")
        self.assertIn("color:var(--orange-text)", labels)
        self.assertIn(".build-band p", CSS)
        for selector in (".learn-more", ".blog-card-link", ".credential-value", ".faq-question .icon", ".service-card::after"):
            self.assertIn("color:var(--orange-text)", css_rule(CSS, selector), selector)

    def test_footer_has_no_visible_h4_headings(self):
        for page in HTML_PAGES:
            source = page.read_text(encoding="utf-8")
            visible_h4 = re.findall(r"<h4\b(?![^>]*\bhidden\b)[^>]*>", source, re.I)
            self.assertEqual(visible_h4, [], page.relative_to(ROOT).as_posix())
            self.assertEqual(source.count('<strong class="footer-heading">'), 4, page.relative_to(ROOT).as_posix())

    def test_every_page_links_a_32_pixel_favicon(self):
        icon = ROOT / "favicon.ico"
        self.assertTrue(icon.is_file())
        data = icon.read_bytes()
        reserved, kind, count = struct.unpack_from("<HHH", data)
        self.assertEqual((reserved, kind), (0, 1))
        self.assertGreaterEqual(count, 1)
        width, height = struct.unpack_from("<BB", data, 6)
        self.assertEqual(width or 256, 32)
        self.assertEqual(height or 256, 32)
        for page in HTML_PAGES:
            source = page.read_text(encoding="utf-8")
            self.assertIn('<link rel="icon" href="/favicon.ico" type="image/x-icon">', source, page.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    unittest.main()

import hashlib
import re
import struct
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
HTML_PAGES = sorted(ROOT.rglob("*.html"))


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
                'src="/images/logo-sm.png"',
                page.read_text(encoding="utf-8"),
                page,
            )

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

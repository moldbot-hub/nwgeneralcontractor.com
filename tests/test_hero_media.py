import hashlib
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def site_html_pages() -> list[Path]:
    return sorted(
        [
            *ROOT.glob("*.html"),
            *ROOT.glob("areas/*.html"),
            *ROOT.glob("blog/*.html"),
            *ROOT.glob("services/*.html"),
        ]
    )


class Element:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []


class DocumentParser(HTMLParser):
    VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.root = Element("document", [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs)
        self.stack[-1].children.append(element)
        if tag not in self.VOID_ELEMENTS:
            self.stack.append(element)

    def handle_endtag(self, tag):
        if len(self.stack) == 1 or self.stack[-1].tag != tag:
            raise AssertionError(f"unexpected closing tag: {tag}")
        self.stack.pop()


def walk(element):
    yield element
    for child in element.children:
        yield from walk(child)


def classes(element):
    return set(element.attrs.get("class", "").split())


def asset_hash(relative_path):
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()[:8]


class WorkshopHeroTests(unittest.TestCase):
    """Catches a return to generated hero media or a flattened blueprint hero."""

    def setUp(self):
        self.source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.parser = DocumentParser()
        self.parser.feed(self.source)
        self.parser.close()

    def test_home_hero_uses_three_blueprint_planes_and_no_video(self):
        hero = next(e for e in walk(self.parser.root) if e.tag == "section" and "home-hero" in classes(e))
        stage = next(e for e in walk(hero) if "blueprint-stage" in classes(e))
        descendants = list(walk(stage))
        self.assertTrue(any("blueprint-grid" in classes(e) for e in descendants))
        self.assertTrue(any("dimension-frame" in classes(e) for e in descendants))
        self.assertTrue(any("blueprint-drawing" in classes(e) for e in descendants))
        self.assertFalse(any(e.tag == "video" for e in walk(hero)))
        self.assertNotIn("/assets/identity", self.source)

    def test_home_hero_has_owner_identity_and_stable_portrait_dimensions(self):
        identity = next(e for e in walk(self.parser.root) if "hero-identity" in classes(e))
        portrait = next(e for e in walk(identity) if e.tag == "img")
        self.assertEqual(portrait.attrs.get("src", "").split("?", 1)[0], "/images/david-headshot.jpg")
        self.assertEqual(portrait.attrs.get("width"), "600")
        self.assertEqual(portrait.attrs.get("height"), "750")
        self.assertIn("David", portrait.attrs.get("alt", ""))
        self.assertIn("NWSTYSH768DA", self.source)

    def test_social_card_is_blueprint_png_with_correct_dimensions(self):
        card = ROOT / "assets" / "og.png"
        self.assertTrue(card.is_file())
        with Image.open(card) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (1200, 630))
        expected = f"/assets/og.png?v={asset_hash('assets/og.png')}"
        for page in site_html_pages():
            source = page.read_text(encoding="utf-8")
            self.assertIn(f'<meta property="og:image" content="https://www.nwgeneralcontractor.com{expected}">', source, page)
            self.assertIn(f'<meta name="twitter:image" content="https://www.nwgeneralcontractor.com{expected}">', source, page)

    def test_ui_has_blueprint_motion_but_no_media_loader_or_counters(self):
        ui = (ROOT / "js" / "ui.js").read_text(encoding="utf-8")
        self.assertIn(".blueprint-grid", ui)
        self.assertIn(".dimension-frame", ui)
        self.assertIn(".blueprint-drawing", ui)
        self.assertIn("prefers-reduced-motion", ui)
        self.assertNotIn("hero-media", ui)
        self.assertNotIn("data-count", ui)
        self.assertNotRegex(ui, re.compile(r"createElement\(['\"]source"))


if __name__ == "__main__":
    unittest.main()

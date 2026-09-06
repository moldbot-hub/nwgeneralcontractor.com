import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.stamp_assets import stamp_assets


def hash8(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


class StampAssetsTests(unittest.TestCase):
    def test_stamps_local_runtime_assets_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("assets/fonts", "assets", "css", "images", "js"):
                (root / folder).mkdir(parents=True, exist_ok=True)

            (root / "assets/fonts/display.woff2").write_bytes(b"font")
            (root / "assets/og.png").write_bytes(b"og")
            (root / "images/portrait.jpg").write_bytes(b"portrait")
            (root / "js/ui.js").write_text("ui", encoding="utf-8")
            style = root / "css/style.css"
            style.write_text("@font-face{src:url('/assets/fonts/display.woff2?v=stale')}", encoding="utf-8")
            page = root / "index.html"
            page.write_text(
                '<link rel="stylesheet" href="/css/style.css?v=stale">\n'
                '<link rel="preload" href="/assets/fonts/display.woff2?v=stale" as="font">\n'
                '<meta property="og:image" content="https://nwgeneralcontractor.com/assets/og.png?v=stale">\n'
                '<img src="/images/portrait.jpg?v=stale">\n'
                '<script src="/js/ui.js?v=stale"></script>\n',
                encoding="utf-8",
            )

            self.assertEqual(1, stamp_assets(root))
            result = page.read_text(encoding="utf-8")
            self.assertIn(f"/css/style.css?v={hash8(style)}", result)
            self.assertIn(f"/assets/fonts/display.woff2?v={hash8(root / 'assets/fonts/display.woff2')}", result)
            self.assertIn(f"/assets/og.png?v={hash8(root / 'assets/og.png')}", result)
            self.assertIn(f"/images/portrait.jpg?v={hash8(root / 'images/portrait.jpg')}", result)
            self.assertIn(f"/js/ui.js?v={hash8(root / 'js/ui.js')}", result)
            first = page.read_bytes()

            self.assertEqual(1, stamp_assets(root))
            self.assertEqual(first, page.read_bytes())


if __name__ == "__main__":
    unittest.main()

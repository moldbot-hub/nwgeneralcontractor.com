import unittest

from tools.workshop_migrate import replace_header_block


class HeaderMigrationTests(unittest.TestCase):
    """Catches migrations that abort on pages whose original chrome lacks a top bar."""

    def test_replaces_header_when_legacy_top_bar_is_absent(self):
        source = '<body>\n<header><div>compact 404 header</div></header>\n<main>Keep me</main>'

        migrated, count = replace_header_block(source, '<header>Workshop</header>')

        self.assertEqual(count, 1)
        self.assertIn('<header>Workshop</header>', migrated)
        self.assertIn('<main>Keep me</main>', migrated)
        self.assertNotIn('compact 404 header', migrated)

    def test_replaces_legacy_top_bar_and_header_as_one_block(self):
        source = '<body>\n<div class="top-bar"><div>Legacy</div></div>\n<header>Old</header>\n<main>Keep me</main>'

        migrated, count = replace_header_block(source, '<header>Workshop</header>')

        self.assertEqual(count, 1)
        self.assertNotIn('Legacy', migrated)
        self.assertNotIn('<header>Old</header>', migrated)
        self.assertIn('<main>Keep me</main>', migrated)

    def test_repeated_header_refresh_is_idempotent(self):
        source = '<body>\n<div class="top-bar">Current</div>\n<header>Current</header>\n<main>Keep me</main>'
        replacement = '\n<div class="top-bar">Workshop</div>\n<header>Workshop</header>\n'

        first, _ = replace_header_block(source, replacement)
        second, _ = replace_header_block(first, replacement)

        self.assertEqual(second, first)


if __name__ == '__main__':
    unittest.main()

import unittest

from site_audit import resolve_local


class InternalTargetNormalizationTests(unittest.TestCase):
    """Catches false content-drift failures for equivalent directory URLs."""

    def test_normalizes_relative_directory_to_its_index(self):
        self.assertEqual(resolve_local('index.html', 'blog/'), ('blog/index.html', ''))

    def test_normalizes_parent_directory_to_root_index(self):
        self.assertEqual(resolve_local('blog/post.html', '../'), ('index.html', ''))


if __name__ == '__main__':
    unittest.main()

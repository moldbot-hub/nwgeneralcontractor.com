import unittest

from site_audit import is_intentionally_eager_image, resolve_local


class InternalTargetNormalizationTests(unittest.TestCase):
    """Catches false content-drift failures for equivalent directory URLs."""

    def test_normalizes_relative_directory_to_its_index(self):
        self.assertEqual(resolve_local('index.html', 'blog/'), ('blog/index.html', ''))

    def test_normalizes_parent_directory_to_root_index(self):
        self.assertEqual(resolve_local('blog/post.html', '../'), ('index.html', ''))


class ImageLoadingPolicyTests(unittest.TestCase):
    def test_allows_only_known_above_fold_or_logo_images_to_skip_lazy_loading(self):
        self.assertTrue(is_intentionally_eager_image('/images/logo-sm.png', {'logo-img'}))
        self.assertTrue(is_intentionally_eager_image('/assets/hero-poster.jpg', {'hero-media__poster'}))
        self.assertFalse(is_intentionally_eager_image('/images/project.jpg', {'project-photo'}))
        self.assertFalse(is_intentionally_eager_image('/assets/poster.jpg', {'hero-media'}))


if __name__ == '__main__':
    unittest.main()

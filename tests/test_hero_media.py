import json
import subprocess
import textwrap
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    def close(self):
        super().close()
        if len(self.stack) != 1:
            raise AssertionError(f"unclosed tag: {self.stack[-1].tag}")


def walk(element):
    yield element
    for child in element.children:
        yield from walk(child)


def classes(element):
    return set(element.attrs.get("class", "").split())


def css_rule(source, selector):
    import re

    match = re.search(r"(?:^|})\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", source)
    if not match:
        raise AssertionError(f"missing CSS rule for {selector}")
    return "".join(match.group(1).split())


def composite(foreground, background, alpha):
    return tuple(alpha * front + (1 - alpha) * back for front, back in zip(foreground, background))


def luminance(rgb):
    channels = [channel / 255 for channel in rgb]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class HeroMediaTests(unittest.TestCase):
    def test_home_hero_starts_with_an_accessible_source_free_media_layer(self):
        parser = DocumentParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        parser.close()

        home_hero = next(element for element in walk(parser.root) if element.tag == "section" and "home-hero" in classes(element))
        media = home_hero.children[0]
        self.assertEqual((media.tag, classes(media), media.attrs.get("aria-hidden")), ("div", {"hero-media"}, "true"))
        self.assertEqual([child.tag for child in media.children], ["img", "video"])

        poster, video = media.children
        self.assertEqual(classes(poster), {"hero-media__poster"})
        self.assertEqual(poster.attrs.get("src"), "/assets/hero-poster.jpg")
        self.assertEqual(poster.attrs.get("srcset"), "/assets/hero-poster-640.jpg 640w, /assets/hero-poster.jpg 1280w")
        self.assertEqual(poster.attrs.get("sizes"), "100vw")
        self.assertEqual(poster.attrs.get("width"), "1280")
        self.assertEqual(poster.attrs.get("height"), "720")
        self.assertEqual(poster.attrs.get("alt"), "")
        self.assertEqual(poster.attrs.get("decoding"), "async")
        self.assertEqual(poster.attrs.get("fetchpriority"), "low")

        self.assertEqual(classes(video), {"hero-media__video"})
        for attribute in ("muted", "loop", "playsinline"):
            self.assertIn(attribute, video.attrs)
        self.assertEqual(video.attrs.get("preload"), "none")
        self.assertEqual(video.attrs.get("poster"), "/assets/hero-poster.jpg")
        self.assertEqual(video.attrs.get("width"), "1280")
        self.assertEqual(video.attrs.get("height"), "720")
        self.assertEqual(video.attrs.get("aria-hidden"), "true")
        self.assertEqual(video.attrs.get("tabindex"), "-1")
        self.assertFalse(any(element.tag == "source" for element in walk(video)))

    def test_media_layer_is_behind_content_and_video_respects_css_preferences(self):
        css = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
        media = css_rule(css, ".hero-media")
        self.assertIn("position:absolute", media)
        self.assertIn("inset:0", media)
        self.assertIn("overflow:hidden", media)
        self.assertIn("z-index:0", media)
        overlay = css_rule(css, ".hero-media::after")
        self.assertIn("linear-gradient(90deg,rgba(20,20,20,.72)0%,rgba(20,20,20,.72)55%,rgba(20,20,20,.55)100%)", overlay)
        self.assertIn("object-fit:cover", css_rule(css, ".hero-media__poster,.hero-media__video"))
        self.assertIn("z-index:1", css_rule(css, ".home-hero .hero-layout"))
        stage = css_rule(css, ".home-hero .blueprint-stage")
        self.assertIn("background:rgba(24,24,24,.4)", stage)

        poster_average = (137, 120, 103)
        charcoal = (20, 20, 20)
        stage_charcoal = (24, 24, 24)
        orange = (255, 106, 19)
        copy_background = composite(charcoal, poster_average, 0.72)
        drawing_background = composite(stage_charcoal, composite(charcoal, poster_average, 0.55), 0.4)
        self.assertGreaterEqual(contrast(orange, copy_background), 4.5)
        self.assertGreaterEqual(contrast(orange, drawing_background), 4.5)
        video = css_rule(css, ".hero-media__video")
        self.assertIn("opacity:0", video)
        self.assertIn("opacity600ms", video.replace(":", ""))
        self.assertIn("opacity:1", css_rule(css, ".hero-media__video.is-playing"))
        self.assertIn(".hero-media__video{display:none}", css.replace(" ", "").split("@media(max-width:719px)", 1)[1])
        self.assertIn(".hero-media__video{display:none", css.replace(" ", "").split("@media(prefers-reduced-motion:reduce)", 1)[1])

    def test_video_source_is_added_after_load_only_for_eligible_visitors(self):
        harness = textwrap.dedent(
            r"""
            const fs = require('fs');
            const vm = require('vm');
            const uiSource = fs.readFileSync(process.argv[1], 'utf8');

            async function exercise(options) {
              const windowListeners = {};
              const videoListeners = {};
              const classes = [];
              let loadCalls = 0;
              let playCalls = 0;
              const video = {
                children: [],
                classList: { add(name) { classes.push(name); } },
                addEventListener(name, callback) { videoListeners[name] = callback; },
                appendChild(child) { this.children.push(child); },
                load() { loadCalls += 1; },
                play() { playCalls += 1; return Promise.resolve(); }
              };
              const document = {
                querySelectorAll() { return []; },
                querySelector(selector) { return selector === '.hero-media__video' ? video : null; },
                createElement(tag) { return { tagName: tag.toUpperCase() }; }
              };
              const window = {
                innerWidth: options.width,
                matchMedia(query) {
                  const matches = query.includes('no-preference') ? !options.reduced : options.reduced;
                  return { matches, addEventListener() {} };
                },
                addEventListener(name, callback) { windowListeners[name] = callback; }
              };
              const context = {
                document,
                navigator: { connection: { saveData: options.saveData } },
                requestAnimationFrame() {},
                window
              };
              vm.runInNewContext(uiSource, context);
              const beforeLoad = video.children.length;
              if (windowListeners.load) windowListeners.load();
              await Promise.resolve();
              return {
                beforeLoad,
                source: video.children[0] || null,
                loadCalls,
                playCalls,
                classes,
                canplayListener: Boolean(videoListeners.canplay)
              };
            }

            (async () => {
              const results = {
                eligible: await exercise({ width: 1280, reduced: false, saveData: false }),
                narrow: await exercise({ width: 719, reduced: false, saveData: false }),
                reduced: await exercise({ width: 1280, reduced: true, saveData: false }),
                saveData: await exercise({ width: 1280, reduced: false, saveData: true })
              };
              process.stdout.write(JSON.stringify(results));
            })().catch(error => { console.error(error); process.exit(1); });
            """
        )
        result = subprocess.run(
            ["node", "-e", harness, str(ROOT / "js" / "ui.js")],
            check=True,
            capture_output=True,
            text=True,
        )
        states = json.loads(result.stdout)
        eligible = states["eligible"]
        self.assertEqual(eligible["beforeLoad"], 0)
        self.assertEqual(eligible["source"]["src"], "/assets/hero.mp4")
        self.assertEqual(eligible["source"]["type"], "video/mp4")
        self.assertEqual((eligible["loadCalls"], eligible["playCalls"]), (1, 1))
        self.assertTrue(eligible["canplayListener"])
        self.assertIn("is-playing", eligible["classes"])
        for name in ("narrow", "reduced", "saveData"):
            self.assertIsNone(states[name]["source"], name)
            self.assertEqual((states[name]["loadCalls"], states[name]["playCalls"]), (0, 0), name)


if __name__ == "__main__":
    unittest.main()

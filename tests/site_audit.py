#!/usr/bin/env python3
"""Capture and verify the static site's content and redesign contracts."""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import posixpath
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "tests" / "baseline-content.json"
SITE_HOSTS = {"nwgeneralcontractor.com", "www.nwgeneralcontractor.com"}
EXPECTED_LEGAL = (
    "© 2026 NW Style Homes 1 LLC, doing business as NW General Contractor · "
    "Washington State registered general contractor NWSTYSH768DA · "
    "Contractor disclosure statement"
)
EXPECTED_TOP = "Registered, bonded and insured · WA contractor NWSTYSH768DA"
FORBIDDEN = ("NW General Contractor LLC", "NW Premier")
HERO_IMAGES = {
    "adu-hero.jpg", "bathroom-hero.jpg", "carpentry-hero.jpg",
    "deck-hero.jpg", "fencing-hero.jpg", "flooring-hero.jpg",
    "foundation-hero.jpg", "garage-hero.jpg", "home-additions-hero.jpg",
    "kitchen-hero.jpg", "outdoor-living-hero.jpg", "painting-hero.jpg",
    "patio-hero.jpg", "roofing-hero.jpg", "siding-hero.jpg",
    "whole-home-hero.jpg", "windows-hero.jpg",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(value)).strip()


def page_paths() -> list[Path]:
    return sorted(ROOT.rglob("*.html"), key=lambda path: path.as_posix())


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def strip_global_chrome(source: str, rel: str) -> str:
    source = re.sub(r"<head\b[\s\S]*?</head>", "", source, flags=re.I)
    source = re.sub(r"<div\s+class=[\"']top-bar[\"'][\s\S]*?</div>\s*</div>\s*</div>", "", source, count=1, flags=re.I)
    source = re.sub(r"<header\b[\s\S]*?</header>", "", source, count=1, flags=re.I)
    source = re.sub(r"<footer\b[\s\S]*?</footer>", "", source, count=1, flags=re.I)
    source = re.sub(r"<div\s+class=[\"']mobile-bottom-cta[\"'][\s\S]*?</div>", "", source, flags=re.I)
    if rel == "index.html":
        source = re.sub(r"<section\s+class=[\"']hero[\"'][\s\S]*?</section>", "", source, count=1, flags=re.I)
    return source


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "svg", "template", "noscript"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg", "template", "noscript"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            value = normalize_text(data)
            if value:
                self.parts.append(value)


class AttributeCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.forms: list[dict[str, object]] = []
        self._form: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.add(data["id"])
        for attr in ("href", "src"):
            if data.get(attr):
                self.refs.append((tag, data[attr], data))
        if tag == "form":
            self._form = {
                "id": data.get("id", ""),
                "class": data.get("class", ""),
                "action": data.get("action", ""),
                "fields": [],
            }
            self.forms.append(self._form)
        elif tag in {"input", "select", "textarea", "button"} and self._form is not None:
            field = {
                "tag": tag,
                "name": data.get("name", ""),
                "id": data.get("id", ""),
                "type": data.get("type", ""),
                "required": "required" in data,
            }
            self._form["fields"].append(field)  # type: ignore[index]

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self._form = None


def collect(source: str) -> AttributeCollector:
    parser = AttributeCollector()
    parser.feed(source)
    return parser


def text_segments(source: str, rel: str) -> list[str]:
    parser = TextCollector()
    parser.feed(strip_global_chrome(source, rel))
    seen: set[str] = set()
    result: list[str] = []
    for part in parser.parts:
        if len(part) >= 3 and part not in seen:
            seen.add(part)
            result.append(part)
    return result


def json_ld(source: str) -> list[object]:
    blocks = re.findall(
        r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>([\s\S]*?)</script>",
        source,
        flags=re.I,
    )
    return [json.loads(block) for block in blocks]


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def resolve_local(page_rel: str, value: str) -> tuple[str | None, str]:
    split = urlsplit(html_lib.unescape(value.strip()))
    if split.scheme in {"tel", "mailto", "javascript", "data"}:
        return None, ""
    if split.scheme in {"http", "https"}:
        if split.hostname not in SITE_HOSTS:
            return None, ""
        raw_path = split.path or "/"
    elif split.scheme or value.startswith("//"):
        return None, ""
    else:
        raw_path = split.path
    directory_form = raw_path.endswith("/")
    if not raw_path:
        target = page_rel
    elif raw_path.startswith("/"):
        target = raw_path.lstrip("/")
    else:
        target = posixpath.normpath(posixpath.join(posixpath.dirname(page_rel), raw_path))
    target = unquote(target)
    if target in {"", "."} or directory_form:
        target = posixpath.join(target, "index.html")
    target = posixpath.normpath(target)
    return target, unquote(split.fragment)


def is_intentionally_eager_image(src: str, class_names: set[str]) -> bool:
    """Return whether a known above-fold image may omit loading=lazy."""
    return "logo" in src.lower() or "hero-media__poster" in class_names


def internal_targets(source: str, rel: str) -> list[str]:
    result: set[str] = set()
    for _tag, value, _attrs in collect(source).refs:
        target, fragment = resolve_local(rel, value)
        if target is not None:
            result.add(target + (f"#{fragment}" if fragment else ""))
    return sorted(result)


def canonicalize_stored_target(value: str) -> str:
    """Normalize directory spellings produced by the original capture version."""
    target, separator, fragment = value.partition("#")
    target = posixpath.normpath(target)
    candidate = ROOT.joinpath(*target.split("/"))
    if candidate.is_dir():
        target = posixpath.join(target, "index.html")
    return target + (separator + fragment if separator else "")


def extract_between(source: str, start: str, end: str) -> str:
    match = re.search(start + r"([\s\S]*?)" + end, source, flags=re.I)
    return match.group(1) if match else ""


def capture() -> int:
    pages = page_paths()
    data: dict[str, object] = {
        "version": 1,
        "page_count": len(pages),
        "protected_hashes": {
            "js/main.js": sha256(ROOT / "js" / "main.js"),
            "js/tracking.js": sha256(ROOT / "js" / "tracking.js"),
        },
        "pages": {},
        "blog_article_hashes": {},
    }
    for path in pages:
        rel = relative(path)
        source = path.read_text(encoding="utf-8")
        parser = collect(source)
        data["pages"][rel] = {  # type: ignore[index]
            "text_segments": text_segments(source, rel),
            "json_ld": [canonical_json(item) for item in json_ld(source)],
            "internal_targets": internal_targets(source, rel),
            "forms": parser.forms,
        }
        if rel.startswith("blog/") and rel != "blog/index.html":
            article = extract_between(
                source,
                r'<div\s+class=["\']content-main article-content["\']>',
                r'<div\s+class=["\']sidebar["\']>',
            )
            data["blog_article_hashes"][rel] = hashlib.sha256(article.encode()).hexdigest()  # type: ignore[index]
    disclosure = (ROOT / "contractor-disclosure.html").read_text(encoding="utf-8")
    disclosure_body = extract_between(disclosure, r'<section\s+class=["\']content-section["\'][^>]*>', r"</section>")
    data["protected_hashes"]["contractor-disclosure-body"] = hashlib.sha256(disclosure_body.encode()).hexdigest()  # type: ignore[index]
    BASELINE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"CAPTURE PASS: {len(pages)} HTML pages recorded in {relative(BASELINE)}")
    print("Protected hashes: js/main.js, js/tracking.js, disclosure body, 14 blog article bodies")
    return 0


def iter_objects(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_objects(child)


def selector_report(source: str, combined_html: str) -> list[tuple[str, int, str]]:
    selectors: list[str] = []
    for match in re.finditer(r"querySelector(?:All)?\(\s*(['\"])(.*?)\1\s*\)", source):
        selectors.append(match.group(2))
    for match in re.finditer(r"getElementById\(\s*(['\"])(.*?)\1\s*\)", source):
        selectors.append("#" + match.group(2))
    selectors = list(dict.fromkeys(selectors))
    class_values = re.findall(r'\bclass=["\']([^"\']*)["\']', combined_html, re.I)

    def class_count(token: str) -> int:
        return sum(token in value.split() for value in class_values)

    reports: list[tuple[str, int, str]] = []
    for selector in selectors:
        bases = [item.strip() for item in selector.split(",")]
        count = 0
        note = "static"
        for base in bases:
            if ".active" in base:
                base = base.replace(".active", "")
                note = "base target; .active is runtime state"
            class_matches = re.findall(r"\.([a-zA-Z0-9_-]+)", base)
            name_matches = re.findall(r'\[name=["\']([^"\']+)', base)
            tag_match = re.match(r"^[a-zA-Z][a-zA-Z0-9-]*", base)
            if name_matches:
                count += sum(len(re.findall(rf'\bname=["\']{re.escape(name)}["\']', combined_html, re.I)) for name in name_matches)
            elif 'action*="formspree.io"' in base:
                count += len(re.findall(r'<form\b[^>]*action=["\'][^"\']*formspree\.io[^"\']*["\']', combined_html, re.I))
            elif class_matches:
                token = class_matches[-1]
                count += class_count(token)
            elif base == 'a[href^="#"]':
                count += len(re.findall(r'<a\b[^>]*href=["\']#', combined_html, re.I))
            elif '[type="submit"]' in base and tag_match:
                count += len(re.findall(rf'<{tag_match.group(0)}\b[^>]*type=["\']submit["\']', combined_html, re.I))
            elif tag_match:
                count += len(re.findall(rf"<{tag_match.group(0)}\b", combined_html, re.I))
        if selector == '[name="company_website"]':
            note = "injected into each matched form at runtime when absent"
        elif selector == '[name="sms_optin"], [name="sms_consent"]':
            note = "one static consent block; injected at runtime on other forms"
        reports.append((selector, count, note))
    return reports


def verify() -> int:
    if not BASELINE.exists():
        print("VERIFY ERROR: baseline missing; run capture first", file=sys.stderr)
        return 2
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    errors: list[str] = []
    pages = page_paths()
    rels = [relative(path) for path in pages]
    if len(pages) != 48:
        errors.append(f"expected 48 HTML pages, found {len(pages)}")
    if set(rels) != set(baseline["pages"]):
        errors.append("HTML URL set differs from baseline")

    if sha256(ROOT / "js" / "main.js") != baseline["protected_hashes"]["js/main.js"]:
        errors.append("js/main.js changed from baseline")
    if sha256(ROOT / "js" / "tracking.js") != baseline["protected_hashes"]["js/tracking.js"]:
        errors.append("js/tracking.js changed from baseline")

    broken: list[str] = []
    json_count = 0
    general_count = 0
    combined_parts: list[str] = []
    selector_html_parts: list[str] = []
    for path in pages:
        rel = relative(path)
        source = path.read_text(encoding="utf-8")
        combined_parts.append(source)
        selector_html_parts.append(source)
        normalized = normalize_text(re.sub(r"<[^>]+>", " ", source))
        if EXPECTED_LEGAL not in normalized:
            errors.append(f"{rel}: exact footer legal line missing")
        if EXPECTED_TOP not in normalized:
            errors.append(f"{rel}: exact registration top bar missing")
        if 'href="/contractor-disclosure.html"' not in source and "href='/contractor-disclosure.html'" not in source:
            errors.append(f"{rel}: root disclosure link missing")
        if "NWSTYSH768DA" not in source:
            errors.append(f"{rel}: registration identifier missing")
        if "workshop-page" not in source:
            errors.append(f"{rel}: workshop page class missing")
        if "/js/ui.js" not in source:
            errors.append(f"{rel}: /js/ui.js missing")
        for name in FORBIDDEN:
            if name in source:
                errors.append(f"{rel}: forbidden name {name!r}")

        try:
            blocks = json_ld(source)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON-LD parse error: {exc}")
            blocks = []
        json_count += len(blocks)
        final_json = {canonical_json(item) for item in blocks}
        for item in baseline["pages"][rel]["json_ld"]:
            if item not in final_json:
                errors.append(f"{rel}: baseline JSON-LD block changed or removed")
        contractors = [
            obj for block in blocks for obj in iter_objects(block)
            if obj.get("@type") == "GeneralContractor"
        ]
        valid_contractors = []
        for obj in contractors:
            identifier = obj.get("identifier", {})
            if isinstance(identifier, dict):
                identifier_value = identifier.get("value")
            else:
                identifier_value = identifier
            if (
                obj.get("name") == "NW General Contractor"
                and obj.get("legalName") == "NW Style Homes 1 LLC"
                and identifier_value == "NWSTYSH768DA"
            ):
                valid_contractors.append(obj)
        if not valid_contractors:
            errors.append(f"{rel}: valid GeneralContractor JSON-LD block missing")
        general_count += len(valid_contractors)

        final_visible = normalize_text(" ".join(text_segments(source, rel)))
        missing_segments = [
            item for item in baseline["pages"][rel]["text_segments"]
            if normalize_text(item) not in final_visible
        ]
        if missing_segments:
            preview = " | ".join(missing_segments[:3])
            errors.append(f"{rel}: {len(missing_segments)} baseline text segment(s) missing: {preview[:240]}")

        final_targets = set(internal_targets(source, rel))
        baseline_targets = {canonicalize_stored_target(item) for item in baseline["pages"][rel]["internal_targets"]}
        missing_targets = baseline_targets - final_targets
        if missing_targets:
            errors.append(f"{rel}: baseline internal targets missing: {', '.join(sorted(missing_targets)[:6])}")

        final_forms = collect(source).forms
        for old_form in baseline["pages"][rel]["forms"]:
            old_fields = {(f["tag"], f["name"], f["id"], f["type"]) for f in old_form["fields"]}
            if not any(old_fields.issubset({(f["tag"], f["name"], f["id"], f["type"]) for f in new_form["fields"]}) for new_form in final_forms):
                errors.append(f"{rel}: baseline form field contract missing")

        parsed = collect(source)
        for tag, value, attrs in parsed.refs:
            target, fragment = resolve_local(rel, value)
            if target is None:
                if tag in {"script", "img"} or (tag == "link" and attrs.get("rel") == "stylesheet"):
                    split = urlsplit(value)
                    if split.scheme in {"http", "https"}:
                        errors.append(f"{rel}: external asset dependency {value}")
                continue
            target_path = ROOT / Path(target.replace("/", str(Path("/").anchor or "/"))) if False else ROOT.joinpath(*target.split("/"))
            if not target_path.exists():
                broken.append(f"{rel}: {value} -> {target}")
                continue
            if fragment and target_path.suffix.lower() == ".html":
                target_ids = collect(target_path.read_text(encoding="utf-8")).ids
                if fragment not in target_ids:
                    broken.append(f"{rel}: {value} -> missing #{fragment}")

        for match in re.finditer(r"<img\b([^>]*)>", source, flags=re.I):
            attrs = match.group(1)
            if not re.search(r"\bwidth=[\"']\d+[\"']", attrs, re.I) or not re.search(r"\bheight=[\"']\d+[\"']", attrs, re.I):
                errors.append(f"{rel}: img missing numeric width/height")
            src_match = re.search(r"\bsrc=[\"']([^\"']+)", attrs, re.I)
            src = src_match.group(1) if src_match else ""
            class_match = re.search(r"\bclass=[\"']([^\"']*)", attrs, re.I)
            class_names = set(class_match.group(1).split()) if class_match else set()
            if src and not is_intentionally_eager_image(src, class_names) and not re.search(r"\bloading=[\"']lazy[\"']", attrs, re.I):
                errors.append(f"{rel}: below-fold img missing loading=lazy")

    if broken:
        errors.extend([f"broken internal reference: {item}" for item in broken])

    combined = "\n".join(combined_parts)
    for image in HERO_IMAGES:
        if image in combined or image in (ROOT / "css" / "style.css").read_text(encoding="utf-8"):
            errors.append(f"obsolete hero reference remains: {image}")
        if (ROOT / "images" / image).exists():
            errors.append(f"obsolete hero file still exists: images/{image}")

    for rel, expected_hash in baseline["blog_article_hashes"].items():
        source = (ROOT / rel).read_text(encoding="utf-8")
        article = extract_between(
            source,
            r'<div\s+class=["\']content-main article-content["\']>',
            r'<div\s+class=["\']sidebar["\']>',
        )
        if hashlib.sha256(article.encode()).hexdigest() != expected_hash:
            errors.append(f"{rel}: article body markup changed")

    disclosure = (ROOT / "contractor-disclosure.html").read_text(encoding="utf-8")
    disclosure_body = extract_between(disclosure, r'<section\s+class=["\']content-section["\'][^>]*>', r"</section>")
    if hashlib.sha256(disclosure_body.encode()).hexdigest() != baseline["protected_hashes"]["contractor-disclosure-body"]:
        errors.append("contractor-disclosure.html: RCW disclosure body changed")

    index = (ROOT / "index.html").read_text(encoding="utf-8")
    if "ADUs, additions and remodels built to Snohomish County code" not in index:
        errors.append("index.html: required ADU-led H1 missing")
    if len(re.findall(r'class=["\'][^"\']*\bservice-card\b', index)) != 17:
        errors.append("index.html: expected exactly 17 service cards")
    if len(re.findall(r'class=["\'][^"\']*\bprocess-step\b', index)) != 5:
        errors.append("index.html: expected exactly 5 process steps")
    if len(re.findall(r'class=["\'][^"\']*\barea-chip\b', index)) != 9:
        errors.append("index.html: expected exactly 9 area chips")
    for marker in ('id="services"', 'id="process"', 'id="areas"', 'id="credentials"', 'id="guides"', 'id="estimate"'):
        if marker not in index:
            errors.append(f"index.html: section marker {marker} missing")

    for path in (ROOT / "services").glob("*.html"):
        source = path.read_text(encoding="utf-8")
        if f'data-blueprint="{path.stem}"' not in source:
            errors.append(f"{relative(path)}: matching blueprint identifier missing")
        if "service-layout" not in source or "sticky-estimate" not in source:
            errors.append(f"{relative(path)}: service two-column/sticky estimate structure missing")
        if "faq-item" in source and "<details" not in source:
            errors.append(f"{relative(path)}: FAQ details/summary conversion missing")

    for path in (ROOT / "areas").glob("*.html"):
        source = path.read_text(encoding="utf-8")
        if 'data-blueprint="map-pin"' not in source:
            errors.append(f"{relative(path)}: map-pin blueprint block missing")
        if "area-layout" not in source or "sticky-estimate" not in source:
            errors.append(f"{relative(path)}: area two-column/sticky estimate structure missing")

    portfolio = (ROOT / "portfolio.html").read_text(encoding="utf-8")
    if "Real job photos are being added; call for references" not in portfolio:
        errors.append("portfolio.html: honest project-photo statement missing")

    css_path = ROOT / "css" / "style.css"
    ui_path = ROOT / "js" / "ui.js"
    css = css_path.read_text(encoding="utf-8")
    for token in ("#141414", "#e9e6df", "#fbfaf7", "#ff6a13", "#7a8a94", "#1c1c1c", "prefers-reduced-motion"):
        if token not in css:
            errors.append(f"css/style.css: required token {token} missing")
    if css_path.stat().st_size >= 45 * 1024:
        errors.append(f"css/style.css: {css_path.stat().st_size} bytes exceeds 45 KB")
    if not ui_path.exists():
        errors.append("js/ui.js missing")
        ui_size = 0
    else:
        ui_size = ui_path.stat().st_size
        if ui_size >= 8 * 1024:
            errors.append(f"js/ui.js: {ui_size} bytes exceeds 8 KB")

    main_source = (ROOT / "js" / "main.js").read_text(encoding="utf-8")
    selectors = selector_report(main_source, "\n".join(selector_html_parts))
    for selector, count, _note in selectors:
        optional = selector in {".faq-item.active", '[name="company_website"]', '[name="sms_optin"], [name="sms_consent"]', 'input[type="submit"]'}
        if count == 0 and not optional:
            errors.append(f"main.js selector has no source target: {selector}")

    status = "PASS" if not errors else "FAIL"
    print(f"VERIFY {status}: {len(pages)} HTML pages")
    print(f"Internal references: {sum(len(internal_targets(p.read_text(encoding='utf-8'), relative(p))) for p in pages)} checked; broken={len(broken)}")
    print(f"JSON-LD: {json_count} blocks parsed; valid GeneralContractor pages={general_count}/{len(pages)}")
    print(f"Protected content: main.js, tracking.js, disclosure body, {len(baseline['blog_article_hashes'])} blog bodies checked")
    print("main.js selectors:")
    for selector, count, note in selectors:
        print(f"  {selector}: {count} ({note})")
    print(f"Sizes: css/style.css={css_path.stat().st_size} bytes; js/ui.js={ui_size} bytes")
    if errors:
        print(f"Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        return 1
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"capture", "verify"}:
        print("Usage: python tests/site_audit.py [capture|verify]", file=sys.stderr)
        return 2
    return capture() if sys.argv[1] == "capture" else verify()


if __name__ == "__main__":
    raise SystemExit(main())

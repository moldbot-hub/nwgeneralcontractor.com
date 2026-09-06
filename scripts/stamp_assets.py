#!/usr/bin/env python3
"""Refresh eight-character SHA-256 query stamps on local runtime assets."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_HOSTS = {"nwgeneralcontractor.com", "www.nwgeneralcontractor.com"}
ASSET_SUFFIXES = {".css", ".js", ".woff2", ".png", ".jpg", ".jpeg", ".webp", ".svg"}
URL_ATTRIBUTE = re.compile(
    r"(?P<prefix>\b(?:href|src|content)=[\"'])(?P<url>[^\"']+)(?P<suffix>[\"'])",
    re.I,
)
CSS_URL = re.compile(r"(?P<prefix>url\([\"']?)(?P<url>[^\"')]+)(?P<suffix>[\"']?\))", re.I)


def hash8(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def page_paths(root: Path) -> list[Path]:
    return sorted(
        [
            *root.glob("*.html"),
            *root.glob("areas/*.html"),
            *root.glob("blog/*.html"),
            *root.glob("services/*.html"),
        ],
        key=lambda path: path.as_posix(),
    )


def stamped_url(raw: str, root: Path, owner: Path) -> str:
    parsed = urlsplit(raw)
    if parsed.scheme and (parsed.scheme not in {"http", "https"} or parsed.hostname not in SITE_HOSTS):
        return raw
    if not parsed.path or Path(parsed.path).suffix.lower() not in ASSET_SUFFIXES:
        return raw

    decoded_path = unquote(parsed.path)
    if decoded_path.startswith("/"):
        target = root.joinpath(*decoded_path.lstrip("/").split("/"))
    else:
        target = owner.parent.joinpath(*decoded_path.split("/"))
    if not target.is_file():
        return raw

    stamp = hash8(target)
    if re.search(r"(?:^|&)v=[^&]*", parsed.query):
        query = re.sub(r"(^|&)v=[^&]*", rf"\1v={stamp}", parsed.query)
    else:
        query = f"{parsed.query}&v={stamp}" if parsed.query else f"v={stamp}"
    authority = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    return f"{authority}{parsed.path}?{query}{fragment}"


def replace_urls(source: str, pattern: re.Pattern[str], root: Path, owner: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        url = stamped_url(match.group("url"), root, owner)
        return f'{match.group("prefix")}{url}{match.group("suffix")}'

    return pattern.sub(replace, source)


def stamp_assets(root: Path = ROOT) -> int:
    for css_path in sorted((root / "css").rglob("*.css")):
        source = css_path.read_text(encoding="utf-8")
        stamped = replace_urls(source, CSS_URL, root, css_path)
        if stamped != source:
            css_path.write_text(stamped, encoding="utf-8", newline="\n")

    pages = page_paths(root)
    for page in pages:
        source = page.read_text(encoding="utf-8")
        stamped = replace_urls(source, URL_ATTRIBUTE, root, page)
        if stamped != source:
            page.write_text(stamped, encoding="utf-8", newline="\n")
    return len(pages)


def main() -> int:
    count = stamp_assets()
    if count != 48:
        print(f"expected 48 HTML pages, found {count}", file=sys.stderr)
        return 1
    print(f"Asset stamps refreshed: {count} HTML pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

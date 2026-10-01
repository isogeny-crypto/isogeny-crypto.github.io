"""Check internal links in the rendered site (docs/) for missing pages and anchors.

Run after `quarto render`:  python3 scripts/check_links.py
Exits non-zero if any link points at a page or #anchor that doesn't exist,
e.g. [CSIDH](/schemes/key-exchange/csidh.qmd#foundations) when csidh.qmd has
no "Foundations" heading. External (http/https/mailto) links are not checked.
"""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs"

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

pages = {}
for path in SITE.rglob("*.html"):
    if "site_libs" in path.parts:
        continue
    parser = Page()
    parser.feed(path.read_text(encoding="utf-8"))
    pages[path.resolve()] = parser

errors = []
for path, page in sorted(pages.items()):
    for href in page.links:
        url = urlsplit(href)
        if url.scheme or url.netloc or href.startswith("mailto:"):
            continue
        if url.path:
            base = SITE.resolve() if url.path.startswith("/") else path.parent
            target = (base / unquote(url.path).lstrip("/")).resolve()
            if target.is_dir():
                target = target / "index.html"
        else:
            target = path
        if target.suffix != ".html":
            continue  # assets, pdfs, etc.
        rel = path.relative_to(SITE.resolve())
        if target not in pages:
            errors.append(f"{rel}: missing page {href}")
        elif url.fragment and unquote(url.fragment) not in pages[target].ids:
            errors.append(f"{rel}: missing anchor {href}")

if not pages:
    errors.append(f"no pages found in {SITE}; run `npm run build` first")
for e in errors:
    print(e)
print(f"check_links: {len(pages)} pages, {len(errors)} broken internal link(s).")
sys.exit(1 if errors else 0)

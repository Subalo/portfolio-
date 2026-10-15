"""Validate local portfolio links, metadata, accessibility basics and original files."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.references = []
        self.images = []
        self.meta = {}
        self.headings = Counter()
        self.lang = None
        self.blank_rel = []
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "html":
            self.lang = attrs.get("lang")
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in ("a", "link") and "href" in attrs:
            self.links.append(attrs["href"])
        if tag in ("img", "script") and "src" in attrs:
            self.links.append(attrs["src"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "a" and attrs.get("target") == "_blank":
            self.blank_rel.append(attrs.get("rel", ""))
        if tag in ("h1", "h2", "h3", "h4"):
            self.headings[tag] += 1
        if tag == "meta":
            self.meta[attrs.get("name") or attrs.get("property")] = attrs.get("content", "")
        for name in ("aria-labelledby", "aria-controls"):
            if name in attrs:
                self.references.extend(attrs[name].split())

errors = []
html = (ROOT / "index.html").read_text()
page = Page()
page.feed(html)
if page.lang != "en":
    errors.append("The document language must be English.")
if page.headings["h1"] != 1:
    errors.append("The page must have exactly one h1.")
for id_, count in Counter(page.ids).items():
    if count > 1:
        errors.append("Duplicate id: " + id_)
for reference in page.references:
    if reference not in page.ids:
        errors.append("Missing ARIA target: " + reference)
for meta in ("description", "og:title", "og:url", "og:image", "twitter:card"):
    if not page.meta.get(meta):
        errors.append("Missing metadata: " + meta)
for relative in page.links:
    parts = urlsplit(relative)
    if parts.scheme or parts.netloc:
        continue
    target = ROOT / unquote(parts.path) if parts.path else ROOT / "index.html"
    if not target.is_file():
        errors.append("Missing linked file: " + relative)
    elif parts.fragment and target.name == "index.html" and parts.fragment not in page.ids:
        errors.append("Missing anchor: " + relative)
for image in page.images:
    if "alt" not in image:
        errors.append("Missing alt attribute: " + image.get("src", ""))
    for dimension in ("width", "height"):
        if not image.get(dimension, "").isdigit() or int(image[dimension]) <= 0:
            errors.append("Missing or invalid image dimension: " + image.get("src", ""))
if any("noopener" not in rel.split() for rel in page.blank_rel):
    errors.append("A new-tab link is missing noopener.")
for placeholder in ("your.email@example.com", "Lorem ipsum", "Engineering Student"):
    if placeholder in html:
        errors.append("Outdated or placeholder content: " + placeholder)
for name, expected in json.loads((ROOT / "docs/original-attachments.json").read_text()).items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    if actual != expected:
        errors.append("Original attachment changed: " + name)
try:
    ET.parse(ROOT / "sitemap.xml")
    ET.parse(ROOT / "favicon.svg")
except ET.ParseError as exc:
    errors.append("Invalid XML: " + str(exc))
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(page.links)} local/external references inspected; {len(page.ids)} unique anchors; metadata and ARIA targets valid.")
print("PASS: all three original Digital Safe attachments are unchanged.")

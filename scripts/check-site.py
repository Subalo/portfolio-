"""Validate local portfolio links, metadata, accessibility basics and original files."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
import hashlib
import json
import re
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
        self.telephones = []
        self._telephone = None
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
        if tag == "a" and attrs.get("href", "").startswith("tel:"):
            self._telephone = {"href": attrs["href"], "text": ""}
        if tag in ("h1", "h2", "h3", "h4"):
            self.headings[tag] += 1
        if tag == "meta":
            self.meta[attrs.get("name") or attrs.get("property")] = attrs.get("content", "")
        for name in ("aria-labelledby", "aria-controls"):
            if name in attrs:
                self.references.extend(attrs[name].split())
    def handle_data(self, data):
        if self._telephone is not None:
            self._telephone["text"] += data
    def handle_endtag(self, tag):
        if tag == "a" and self._telephone is not None:
            self.telephones.append(self._telephone)
            self._telephone = None

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
try:
    person = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    expected_phone = person["telephone"]
    if not page.telephones:
        errors.append("Missing visible phone link.")
    for phone in page.telephones:
        digits = re.sub(r"\D", "", phone["text"])
        displayed = "+972" + digits[1:] if digits.startswith("0") else "+" + digits
        if phone["href"] != "tel:" + expected_phone or displayed != expected_phone:
            errors.append("Displayed phone, dialing link and metadata do not agree.")
except (AttributeError, KeyError, json.JSONDecodeError) as exc:
    errors.append("Invalid person contact metadata: " + str(exc))
for asset in ("style.css", "site.js"):
    references = [urlsplit(link) for link in page.links if urlsplit(link).path == asset]
    version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:12]
    if len(references) != 1 or parse_qs(references[0].query).get("v") != [version]:
        errors.append("Missing or outdated asset version: " + asset)
css = (ROOT / "style.css").read_text()
for size in re.findall(r"font-size:([^;\n}]+)", css):
    if "px" in size:
        errors.append("Use relative type sizes: " + size)
    if any(float(value) < .75 for value in re.findall(r"([\d.]+)rem", size)):
        errors.append("Text is smaller than the 12 px label baseline: " + size)
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
print("PASS: phone links, contact metadata, asset versions and minimum relative type sizes are valid.")

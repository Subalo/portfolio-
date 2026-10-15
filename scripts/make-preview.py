"""Create an offline visual preview; document downloads use the review branch."""
from pathlib import Path
from html.parser import HTMLParser
import base64
import mimetypes
import re

ROOT = Path(__file__).resolve().parents[1]
ASSET_BASE = "https://raw.githubusercontent.com/Subalo/portfolio-/feature/portfolio-redesign/"

def inline_file(relative):
    data = (ROOT / relative).read_bytes()
    mime = mimetypes.guess_type(relative)[0] or "application/octet-stream"
    return "data:" + mime + ";base64," + base64.b64encode(data).decode()

html = (ROOT / "index.html").read_text()
html = html.replace('<link rel="stylesheet" href="style.css">', "<style>" + (ROOT / "style.css").read_text() + "</style>")
html = html.replace('<script src="site.js" defer></script>', "<script>" + (ROOT / "site.js").read_text() + "</script>")
# Inline script must still execute after the DOM exists in the standalone file.
start = html.index("<script>/* Content")
end = html.index("</script>", start) + len("</script>")
script = html[start:end]
html = html[:start] + html[end:]
html = html.replace("</body>", script + "\n</body>")
def replace(match):
    attribute, value = match.group(1), match.group(2)
    if value.startswith(("assets/images/", "favicon.svg")):
        return attribute + '="' + inline_file(value) + '"'
    if value.endswith((".pdf", ".pptx")) and not value.startswith(("https:", "http:", "data:")):
        return attribute + '="' + ASSET_BASE + value + '"'
    return match.group(0)
html = re.sub(r'(src|href)="([^"]+)"', replace, html)
output = ROOT / "review" / "portfolio-preview.html"
output.parent.mkdir(exist_ok=True)
output.write_text(html)
print(output)

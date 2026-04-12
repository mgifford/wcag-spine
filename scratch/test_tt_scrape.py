from __future__ import annotations
import urllib.request
import re
import sys

def fetch_text(url: str, timeout: int = 30) -> str | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "wcag-spine-sync/1.0 (https://github.com/mgifford/wcag-spine)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except Exception as exc:
        print(f"Error fetching {url}: {exc}")
        return None

def test_scrape():
    url = "https://section508coordinators.github.io/TrustedTester/images.html"
    content = fetch_text(url)
    if not content:
        return

    sc = "1.1.1"
    sc_pattern = sc.replace(".", r"\.")
    
    # Pattern: <td>1.1.1-some-slug</td> \s* <td>7.A</td>
    pattern = r'<td>(' + sc_pattern + r'-[a-zA-Z0-9\-]+)</td>\s*<td>([0-9A-Z\.]+)</td>'
    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
    
    found = False
    for m in matches:
        slug = m.group(1).replace(sc + "-", "").replace("-", " ").title()
        test_id = m.group(2)
        print(f"Found: {test_id} - {slug}")
        found = True
    
    if not found:
        print("Still no luck! Let's try more flexible.")

if __name__ == "__main__":
    test_scrape()

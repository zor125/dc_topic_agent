# src/parse_post.py
from lxml import html

XPATH_CANDIDATES = [
    "//div[contains(@class,'write_div')]",
    "//div[contains(@class,'writing_view_box')]",
    "//div[contains(@class,'write_div') or contains(@class,'writing_view_box')]",
]

def parse_post_content(html_text: str) -> str:
    doc = html.fromstring(html_text)
    for xp in XPATH_CANDIDATES:
        nodes = doc.xpath(xp)
        if nodes:
            text = nodes[0].text_content().strip()
            return " ".join(text.split())
    return ""
import random
import time
import re
from typing import List, Dict
import requests
from lxml import html

GALLERY_ID = "nogada"
LIST_URL = "https://gall.dcinside.com/mgallery/board/lists/?id={gid}&page={page}"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

def fetch_list_page(page: int, delay_min: float = 0.8, delay_max: float = 2.0) -> str:
    """목록 페이지 HTML 가져오기"""
    time.sleep(random.uniform(delay_min, delay_max))
    url = LIST_URL.format(gid=GALLERY_ID, page=page)
    r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
    r.raise_for_status()
    return r.text

def parse_list(html_text: str) -> List[Dict]:
    """목록 HTML에서 글 후보 파싱"""
    doc = html.fromstring(html_text)

    # ✅ 디시가 구조를 바꾸면 여기 XPath가 깨질 수 있음 = 유지보수 포인트(여기만 고치면 됨)
    rows = doc.xpath("//table[contains(@class,'gall_list')]//tr[contains(@class,'ub-content')]")

    items = []
    for row in rows:
        a_list = row.xpath(".//td[contains(@class,'gall_tit')]//a")
        if not a_list:
            continue

        a = a_list[0]
        title = a.text_content().strip()
        href = (a.get("href") or "").strip()
        if not href:
            continue

        m = re.search(r"no=(\d+)", href)
        if not m:
            continue
        doc_id = int(m.group(1))

        v = row.xpath(".//td[contains(@class,'gall_count')]/text()")
        views = 0
        if v:
            vv = v[0].strip().replace(",", "")
            if vv.isdigit():
                views = int(vv)

        cm = re.search(r"\[(\d+)\]\s*$", title)
        comment_count = int(cm.group(1)) if cm else 0

        url = "https://gall.dcinside.com" + href if href.startswith("/") else href

        items.append({
            "doc_id": doc_id,
            "title": title,
            "url": url,
            "views": views,
            "comment_count": comment_count
        })

    return items

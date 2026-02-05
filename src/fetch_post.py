# src/fetch_post.py
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://gall.dcinside.com/",
}

def fetch_post_page(url: str, sleep_sec: float = 0.4) -> str:
    time.sleep(sleep_sec)  # 너무 빠르면 차단 위험
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.text
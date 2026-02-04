import json
from datetime import datetime
from pathlib import Path

from fetch_list_pc import fetch_list_page, parse_list
from cache import init_db, is_seen, mark_seen
from score import score_items

OUT_DIR = Path("data/out")
DEBUG_DIR = Path("data/debug")

def run(pages: int = 2, top_k: int = 20):
    init_db()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    now_iso = now.isoformat(timespec="seconds")
    date_str = now.strftime("%Y-%m-%d")

    all_items = []
    for p in range(1, pages + 1):
        try:
            html_text = fetch_list_page(p)
        except Exception as e:
            print(f"[ERROR] fetch page {p}: {e}")
            continue

        # 디시 구조 바뀌면 이 파일 열어서 XPath 고치면 됨
        (DEBUG_DIR / f"list_page_{p}.html").write_text(html_text, encoding="utf-8")

        items = parse_list(html_text)
        all_items.extend(items)

    # doc_id 기준 중복 제거
    unique = {it["doc_id"]: it for it in all_items}
    deduped = list(unique.values())

    # 이미 본 글은 제외
    fresh = [it for it in deduped if not is_seen(it["doc_id"])]

    scored = score_items(fresh)

    result = {
        "source": "dcinside_nogada",
        "collected_at": now_iso,
        "candidate_count": len(scored),
        "top_recommend": scored[:3],
        "top_candidates": scored[:top_k],
    }

    out_path = OUT_DIR / f"topics_{date_str}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # 오늘 처리한 상위 top_k는 seen 처리
    mark_seen([it["doc_id"] for it in scored[:top_k]], now_iso)

    print(f"[OK] saved: {out_path}")

if __name__ == "__main__":
    run(pages=2, top_k=20)

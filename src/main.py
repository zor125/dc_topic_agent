import json
from datetime import datetime
from pathlib import Path

from fetch_list_pc import fetch_list_page, parse_list
from cache import init_db, is_seen, mark_seen
from score import score_items

from fetch_post import fetch_post_page
from parse_post import parse_post_content
from script_corpus import load_scripts
from content_score import script_match_score

OUT_DIR = Path("data/out")
DEBUG_DIR = Path("data/debug")

def run(pages: int = 10, pool_k: int = 200, content_k: int = 20, top_k: int = 20):
    """
    pages: 목록 페이지 수(많이 긁기)
    pool_k: 1차 점수 기준 후보 풀 크기(많이)
    content_k: 본문 확인할 상위 개수(보통 20)
    top_k: 최종 topics.json에 넣을 개수(보통 20)
    """
    init_db()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    scripts = load_scripts()  # ✅ 내가 쓴 쇼츠 스크립트들(코퍼스)
    if not scripts:
        print("[WARN] data/scripts/*.txt 가 비어있음. script 기반 점수는 0으로 처리됨.")

    now = datetime.now()
    now_iso = now.isoformat(timespec="seconds")
    date_str = now.strftime("%Y-%m-%d")

    # 1) 목록에서 많이 수집
    all_items = []
    for p in range(1, pages + 1):
        try:
            html_text = fetch_list_page(p)
        except Exception as e:
            print(f"[ERROR] fetch page {p}: {e}")
            continue

        (DEBUG_DIR / f"list_page_{p}.html").write_text(html_text, encoding="utf-8")

        items = parse_list(html_text)
        all_items.extend(items)

    # 2) doc_id 기준 중복 제거
    unique = {it["doc_id"]: it for it in all_items}
    deduped = list(unique.values())

    # 3) 이미 본 글 제외
    fresh = [it for it in deduped if not is_seen(it["doc_id"])]

    # 4) 1차 점수(제목/조회/댓글 등)로 스코어링
    scored = score_items(fresh)

    # ✅ 후보 풀(pool_k)만 남기기 (본문 요청 전에 컷)
    scored = scored[:pool_k]

    # 5) 상위 content_k개만 본문 확인 + 스크립트 유사도 2차 점수 반영
    for it in scored[:content_k]:
        try:
            post_html = fetch_post_page(it["url"])
            content = parse_post_content(post_html)
            it["content"] = content

            sim = script_match_score(content, scripts) if scripts else 0.0  # 0.0~1.0

            # score_detail이 없을 수도 있으니 안전하게
            it.setdefault("score_detail", {})
            it["score_detail"]["script_sim"] = round(sim, 4)

            # ✅ 가중치: 유사도 1.0이면 +40점 (원하면 조절)
            it["score"] += int(sim * 40)

        except Exception as e:
            it["content"] = ""
            it.setdefault("score_detail", {})
            it["score_detail"]["script_sim"] = 0.0
            it["score_detail"]["content_error"] = str(e)

    # 6) 본문 점수 반영 후 재정렬
    scored.sort(key=lambda x: x["score"], reverse=True)

    # 7) 결과 저장 (최종 top_k만)
    result = {
        "source": "dcinside_nogada",
        "collected_at": now_iso,
        "candidate_count": len(scored),
        "top_recommend": scored[:3],
        "top_candidates": scored[:top_k],
    }

    out_path = OUT_DIR / f"topics_{date_str}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # ✅ 최종 top_k만 seen 처리
    mark_seen([it["doc_id"] for it in scored[:top_k]], now_iso)

    print(f"[OK] saved: {out_path}")

if __name__ == "__main__":
    run(pages=10, pool_k=200, content_k=20, top_k=20)
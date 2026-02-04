from typing import Dict, List

KEYWORDS = [
    "안전화", "지벤", "K2", "공구", "함마", "힐티", "뿌레카",
    "동바리", "시스템비계", "비계", "샷시", "칸막이", "케이블",
    "용어", "단도리", "오사마리", "데마", "먹통", "레미탈"
]

def keyword_score(title: str) -> int:
    t = title.lower()
    score = 0
    for k in KEYWORDS:
        if k.lower() in t:
            score += 6
    return min(score, 30)

def score_items(items: List[Dict]) -> List[Dict]:
    """
    MVP: 목록에서 안정적으로 뽑히는 '조회/댓글/키워드'로만 점수화
    """
    scored = []
    for it in items:
        views = it.get("views", 0)
        comments = it.get("comment_count", 0)

        react = 0
        if views > 0:
            react += min(30, views // 200)   # 조회 200당 1점, 최대 30
        react += min(30, comments * 4)      # 댓글 1개당 4점, 최대 30

        kw = keyword_score(it.get("title", ""))

        total = min(100, react + kw)

        new_it = dict(it)
        new_it["score"] = total
        new_it["score_detail"] = {"react": react, "keyword": kw}
        scored.append(new_it)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored

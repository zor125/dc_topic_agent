# src/content_score.py
from similarity import cosine_sim

def script_match_score(content: str, scripts: list[str]) -> float:
    if not content or not scripts:
        return 0.0
    return max(cosine_sim(content, s) for s in scripts)
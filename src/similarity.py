# src/similarity.py
import math
import re
from collections import Counter

_token_re = re.compile(r"[0-9A-Za-z가-힣]+")

def tokenize(s: str) -> list[str]:
    return _token_re.findall((s or "").lower())

def cosine_sim(a: str, b: str) -> float:
    ta = Counter(tokenize(a))
    tb = Counter(tokenize(b))
    if not ta or not tb:
        return 0.0

    # dot
    dot = 0
    for k, va in ta.items():
        vb = tb.get(k, 0)
        dot += va * vb

    # norms
    na = math.sqrt(sum(v*v for v in ta.values()))
    nb = math.sqrt(sum(v*v for v in tb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
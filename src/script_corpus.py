# src/script_corpus.py
from pathlib import Path

SCRIPTS_DIR = Path("data/scripts")

def load_scripts() -> list[str]:
    if not SCRIPTS_DIR.exists():
        return []
    texts = []
    for p in sorted(SCRIPTS_DIR.glob("*.txt")):
        texts.append(p.read_text(encoding="utf-8").strip())
    return [t for t in texts if t]
from collections import defaultdict

LEX = {
    "strong_positive": [
        "surge","skyrocket","record high","breakthrough","bull run","soar","rally","moonshot","all-time high"
    ],
    "positive": [
        "gain","rise","growth","adoption","upgrade","partnership","optimistic","recover","momentum","bullish"
    ],
    "strong_negative": [
        "crash","plunge","collapse","scam","hack","breach","lawsuit","fraud","crackdown","ban","meltdown"
    ],
    "negative": [
        "drop","fall","decline","risk","bearish","volatile","uncertainty","warning","pressure","concern"
    ],
    "neutral": [
        "stable","steady","unchanged","hold","consolidate","range-bound","sideways","maintain"
    ],
}

WEIGHTS = {
    "strong_positive": 1.5,
    "positive": 1.0,
    "strong_negative": -2.0,
    "negative": -1.2,
    "neutral": 0.3,
}

def score(text: str) -> float:
    t = (text or "").lower()
    total = 0.0
    for group, terms in LEX.items():
        w = WEIGHTS[group]
        total += sum(t.count(term) for term in terms) * w
    return total

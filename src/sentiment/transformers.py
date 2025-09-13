from functools import lru_cache
from typing import Optional
import os

def _model_id() -> str:
    return os.getenv("HF_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest")

@lru_cache(maxsize=1)
def _pipeline():
    from transformers import pipeline
    return pipeline("sentiment-analysis", model=_model_id(), top_k=None)

def score(text: str) -> Optional[float]:
    try:
        clf = _pipeline()
        res = clf(text or "")[0]
        if isinstance(res, list):  # top_k case
            res = max(res, key=lambda x: x["score"])
        label = res["label"].lower()
        s = float(res["score"])
        if "positive" in label:
            return s
        if "negative" in label:
            return -s
        return 0.0
    except Exception:
        return None

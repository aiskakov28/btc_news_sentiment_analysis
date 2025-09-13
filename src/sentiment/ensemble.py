from typing import Dict, Tuple, Optional
from textblob import TextBlob
from . import vader as _vader
from . import transformers as _hf
from . import indicators as _ind

def analyze(headline: str, summary: str, weights: Dict[str, float], threshold: float) -> Tuple[int, float, Dict]:
    text = f"{headline or ''} {summary or ''}".strip()

    s_vader = _vader.score(text)
    s_tb = TextBlob(text).sentiment.polarity
    s_hf: Optional[float] = _hf.score(text)
    s_lex = _ind.score(text)

    parts = {
        "vader": s_vader,
        "textblob": s_tb,
        "transformer": s_hf if s_hf is not None else 0.0,
        "lexicon": s_lex,
    }

    w_v = weights.get("vader", 0.35)
    w_t = weights.get("textblob", 0.15)
    w_h = weights.get("transformer", 0.35)
    w_l = weights.get("lexicon", 0.15)

    score = w_v * s_vader + w_t * s_tb + w_l * s_lex + (w_h * s_hf if s_hf is not None else 0.0)
    confidence = min(abs(score), 1.0)
    sentiment = 1 if score > threshold else (-1 if score < -threshold else 0)

    return sentiment, confidence, {**parts, "combined": score}

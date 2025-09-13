from src.sentiment import vader, indicators, ensemble

def test_vader_score_range():
    s = vader.score("Bitcoin surges to new record")
    assert -1.0 <= s <= 1.0

def test_indicators_positive_negative():
    pos = indicators.score("massive surge and rally to record high")
    neg = indicators.score("exchange hack causes crash and meltdown")
    assert pos > 0 and neg < 0

def test_ensemble_outputs():
    w = {"vader":0.35,"textblob":0.15,"transformer":0.0,"lexicon":0.5}
    s, c, parts = ensemble.analyze("BTC surges to record high", "bullish rally", w, threshold=0.03)
    assert s in (-1,0,1) and 0 <= c <= 1 and "combined" in parts
